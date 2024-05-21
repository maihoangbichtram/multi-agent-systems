!start.
 
+!start
 <-
  ?name(N);
  .print("OrderPackagerAgent Packaging ", N, ": Starting");
  !askForOrder.
   
+!pack(X)
 <-
  ?name(N);
  .print("OrderPackagerAgent ", N," packaging ", X);
  .packItems(R);
  .wait(R);
  .print("-- OrderPackagerAgent ", N," FINISHED packaging ", X, "--");
  .wait(100);
  !askForOrder.
  
+!askForOrder
 <-
  ?id(ID);
  .print("OrderPackagerAgent availableForJob");
  ?manager(M);
  .send(M, tell, availableForJob(ID)).