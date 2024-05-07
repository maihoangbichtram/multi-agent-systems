import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour,  PeriodicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
import json
import random

NO_OF_PACKAGER_AGENT = 10

class Order:
    def __init__(self, orderId, items = [], shippingAddress = {}):
        self.orderId = orderId
        self.items = items
        self.shippingAddress = shippingAddress
    
    def getModelData(self):
        return {'orderId': self.orderId, 'items': self.items, 'shippingAddress': self.shippingAddress,}

class ShopAgent(Agent):
    class InformBehav(CyclicBehaviour):
        async def on_start(self):
            print("ShopAgent: Starting behaviour . . .")
            self.counter = 0
            
        async def run(self):
            msg = Message(to="order.packager.agent.1@localhost") # Instantiate the message
            msg.set_metadata("performative", "request")
            msg.body = json.dumps(Order(self.counter).getModelData()) # Set the message content            
            await self.send(msg)
            print("ShopAgent: Message sent {}!".format(msg.body))
            self.counter += 1
            
            if self.counter >= 15:
                self.kill(exit_code=10)
                return
            # stop agent from behaviour
            #await self.agent.stop()
    async def setup(self):
        print("ShopAgent started")
        b = self.InformBehav()
        self.add_behaviour(b)

class OrderPackagerAgent(Agent):
    allWaitingMsg = []
    class Packaging(PeriodicBehaviour):
        async def on_start(self):
            print("OrderPackagerAgent Packaging {}: Starting behaviour . . .".format(self.agent.jid))
            self.step = 0
            self.name =  str(self.agent.jid)
            self.id = self.name.split('.')[-1].split('@')[0]
            self.orderId = None
            self.msg = None
        async def run(self):
            def packPakage(items):
                # TODO: gathering items into a box
                return
            
            def getPackageDetail(items):
                packPakage(items)
                # TODO: measure dimensions and weight of packed box
                return {'dimension': [], 'weight': [],}
                
                
            msgBody = {}
            if not self.msg and len(self.agent.allWaitingMsg) > 0:
                print("OrderPackagerAgent Packaging {}: {} jobs in queue ".format(self.agent.jid, len(self.agent.allWaitingMsg)))
                
                self.msg =  self.agent.allWaitingMsg[0]
                self.agent.allWaitingMsg.pop(0)
                msgBody = json.loads(self.msg.body)
                self.orderId = msgBody['orderId']
            if self.msg:
                match self.step:
                    case 0:
                        packageDetail = getPackageDetail(msgBody.items)
                        fwdMsgBody = {}
                        fwdMsg = Message(to="shipping.service.connector@localhost") # Instantiate the message
                        fwdMsg.set_metadata("performative", "cfp")  # Set the "inform" FIPA performative
                        fwdMsgBody['packageDetail'] = packageDetail
                        fwdMsgBody['shippingAddress'] = msgBody['shippingAddress']
                        fwdMsg.body = json.dumps(fwdMsgBody)                    # Set the message content
            
                        await self.send(fwdMsg)
                        self.step = 1
                    case 1:
                        msg = await self.receive(timeout=10) # wait for a message for 10 seconds
                        if msg:
                            print("------------------Order {} - {}-----------------------".format(self.orderId, msg.body))
                            # TODO: attach shipment label to package
                            self.step = 2
                        else:
                            print("OrderPackagerAgent: Did not received any message after 10 seconds")
                    case 2:
                        # TODO submit ready-to-ship package to Logistics Manager
                        self.msg = None
                        self.step = 0                
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("OrderPackagerAgent {}: Starting behaviour . . .".format(self.agent.jid))
            self.name =  str(self.agent.jid)

        async def run(self):
            msg = await self.receive(timeout=10) # wait for a message for 10 seconds
            if msg:
                print("OrderPackagerAgent MyBehav {}: Message received with content: {}".format(self.name, msg.body))
                self.agent.allWaitingMsg.append(msg)
                
        
    async def setup(self):
        print("OrderPackagerAgent starting . . .")
        
        template = Template()
        template.set_metadata("performative", "request")         
        self.b = self.MyBehav()
        self.add_behaviour(self.b, template)
        
        self.packaging =  self.Packaging(period=5)
        template = Template()
        template.set_metadata("performative", "proposal")        
        self.add_behaviour(self.packaging, template)
            
class OrderPackagerAgentManager(Agent):
    class CreateAgent(OneShotBehaviour):
        async def run(self):
            for i in range(1, NO_OF_PACKAGER_AGENT + 1):
                agent = OrderPackagerAgent('order.packager.agent.{}@localhost'.format(i), "test")
                await agent.start(auto_register=True)
    
    async def setup(self):
        print("OrderPackagerAgentManager started")
        self.createAgent = self.CreateAgent()
        self.add_behaviour(self.createAgent)

class ShippingServiceConnectorAgent(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("ShippingServiceConnectorAgent: Starting behaviour . . .")
            self.counter = 0

        async def run(self):
            def registerPackage(shipmentDetail):
                # TODO: pass shipment detail to shipphing service -> tracking id
                return 'FI{}'.format(random.randint(100000000, 999999999))
            
            msg = await self.receive(timeout=10) # wait for a message for 10 seconds
            if msg:
                # print('ShippingServiceConnectorAgent: Message received {}'.format(msg))
                replyBody = json.loads(msg.body)
                shipmentLabel = registerPackage(replyBody)
                reply = msg.make_reply()
                reply.set_metadata("performative", "proposal")
                
                reply.body = shipmentLabel
                await self.send(reply)
            else:
                print("ShippingServiceConnectorAgent: Did not received any message after 10 seconds")
            
            #await self.agent.stop()

    async def setup(self):
        print("ShippingServiceConnectorAgent: Agent starting . . .")
        b = self.MyBehav()
        template = Template()
        template.set_metadata("performative", "cfp")
        self.add_behaviour(b, template)

async def main():
    shippingServiceConnectorAgent = ShippingServiceConnectorAgent("shipping.service.connector@localhost", "test")
    await shippingServiceConnectorAgent.start()
    print("ShippingServiceConnectorAgent started. Check its console to see the output.")
    shippingServiceConnectorAgent.web.start(hostname="localhost", port="10000")    
    
    orderPackagerAgentManager = OrderPackagerAgentManager("order.packager@localhost", "test")
    await orderPackagerAgentManager.start()
    await orderPackagerAgentManager.createAgent.join()
    print("orderPackagerAgentManager started. Check its console to see the output.")
    orderPackagerAgentManager.web.start(hostname="localhost", port="10001")

    shopAgent = ShopAgent("shop.agent@localhost", "test")
    await shopAgent.start()
    print("ShopAgent started. Check its console to see the output.")    
    shopAgent.web.start(hostname="localhost", port="10002")    

    print("Wait until user interrupts with ctrl+C")
    await wait_until_finished(shopAgent)

if __name__ == "__main__":
    spade.run(main())
    #order = Order(1)
    #print(json.dumps(order.getModelData()))