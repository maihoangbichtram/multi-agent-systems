import argparse
import asyncio
import getpass
import random
from datetime import datetime

import spade
from spade.behaviour import PeriodicBehaviour
from spade.template import Template

from spade_bdi.bdi import BDIAgent

class ShopAgent(BDIAgent):
    async def setup(self):
        template = Template(metadata={"performative": "CreateOrder"})
        self.add_behaviour(self.CreateOrder(period=0.1, start_at=datetime.now()), template)
    class CreateOrder(PeriodicBehaviour):
        async def run(self):
            self.agent.bdi.set_belief('order', random.randint(1, 2000))
            
class OrderPackagerAgentManager(BDIAgent):
    def add_custom_actions(self, actions):
        @actions.add_function(".addOrder", (tuple, int, ))
        def _addOrder(orders, newOrder):
            y = list(orders)
            y.append(newOrder)
            return tuple(y)
        
        @actions.add_function(".addPackager", (tuple, int, ))
        def _addPackager(waitingPackagers, packagerID):
            y = list(waitingPackagers)
            y.append('order.packager.agent.{}@{}'.format(packagerID, server))
            return tuple(y)        
        
        @actions.add_function(".fetchFirstItem", (tuple, ))
        def _fetchFirstItem(items):
            y = list(items)
            firstItem = y[0]
            return firstItem
        
        @actions.add_function(".removeFirstItem", (tuple, ))
        def _removeFirstItem(items):
            y = list(items)
            y.pop(0)
            return tuple(y)

class OrderPackagerAgent(BDIAgent):
    def add_custom_actions(self, actions):
        @actions.add_function(".packItems", ())
        def _packItems():
            return random.randint(100, 500)

async def main(server, password):
    orderPackagerManager = OrderPackagerAgentManager("order.packager@{}".format(server), password, "orderPackagerManager.asl")
    orderPackagerManager.bdi.set_belief("shop", "shop.agent@{}".format(server))
    await orderPackagerManager.start()     
    
    agent = OrderPackagerAgent('order.packager.agent.1@{}'.format(server), password, "orderPackager.asl")
    agent.bdi.set_belief("name", "1")
    agent.bdi.set_belief("id", "1")    
    agent.bdi.set_belief("manager", "order.packager@{}".format(server))
    await agent.start()
    
    agent2 = OrderPackagerAgent('order.packager.agent.2@{}'.format(server), password, "orderPackager.asl")
    agent2.bdi.set_belief("name", "2")
    agent2.bdi.set_belief("id", "2")
    agent2.bdi.set_belief("manager", "order.packager@{}".format(server))
    await agent2.start()
    
    agent3 = OrderPackagerAgent('order.packager.agent.3@{}'.format(server), password, "orderPackager.asl")
    agent3.bdi.set_belief("name", "3")
    agent3.bdi.set_belief("id", "3")
    agent3.bdi.set_belief("manager", "order.packager@{}".format(server))
    await agent3.start()
    
    agent4 = OrderPackagerAgent('order.packager.agent.4@{}'.format(server), password, "orderPackager.asl")
    agent4.bdi.set_belief("name", "4")
    agent4.bdi.set_belief("id", "4")
    agent4.bdi.set_belief("manager", "order.packager@{}".format(server))
    await agent4.start()
    
    shop = ShopAgent("shop.agent@{}".format(server), password, "shop.asl")
    shop.bdi.set_belief("orderPackagerManager", "order.packager@{}".format(server))
    await shop.start()     

    await asyncio.sleep(10)
    await shop.stop()
    await orderPackagerManager.stop()
    await agent.stop()
    await agent2.stop()
    await agent3.stop()
    await agent4.stop()
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="XMPP Server")
    parser.add_argument("--password", help="Password")
    args = parser.parse_args()

    if args.server is None:
        server = input("XMPP Server> ")
    else:
        server = args.server

    if args.password is None:
        passwd = getpass.getpass()
    else:
        passwd = args.password
    spade.run(main(server, passwd))