!start.

+!start
 <- 
  .print("ShopAgent: Starting...");
  !sendOrder.

+!sendOrder: order(X)
 <-
  ?orderPackagerManager(M);
  .send(M, tell, newOrder(X));
  .print("ShopAgent sending order...", X);
  -order(X);
  !sendOrder.
  

+!sendOrder: not order(_)
 <-
  .print("Waiting");
  .wait(100);
  !sendOrder.