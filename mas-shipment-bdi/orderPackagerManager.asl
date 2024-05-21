!start.
orders([]).
avalbPackagers([]).

+!start
 <-
  .print("OrderPackagerAgentManager Starting ...").
  
+!assignOrder(Order): avalbPackagers(WP) & .length(WP, WPL) & WPL > 0
 <-
  .fetchFirstItem(WP, WPF);
  .removeFirstItem(WP, WP2);
  -+avalbPackagers(WP2);
  .print("OrderPackagerAgentManager assigned order ", Order, " to agent ", WPF);
  .send(WPF, achieve, pack(Order)).
  
+!assignOrder(Order): avalbPackagers(WP) & not(.length(WP, WPL) & WPL > 0)
 <-
  .print("OrderPackagerAgentManager no waiting packager....");
  ?orders(X);
  .addOrder(X, Order, R);
  -+orders(R);
  .print("OrderPackagerAgentManager orders ", R).
  
+newOrder(Order)[source(S)]
 <-
  !assignOrder(Order).
  
+availableForJob(ID)[source(S)]
 <-
  !assignJob(S, ID).
  
+!assignJob(S, ID): orders(X) & .length(X, L) & L > 0
 <-
  .fetchFirstItem(X, R);
  .removeFirstItem(X, R2);
  -+orders(R2);
  .print("OrderPackagerAgentManager assigned order ", R, " to agent ", S);
  .send(S, achieve, pack(R)).

+!assignJob(S, ID): orders(X) & not(.length(X, L) & L > 0)
 <-
  .print("OrderPackagerAgentManager no available jobs....");
  ?avalbPackagers(WP);
  .addPackager(WP, ID, WPN);
  -+avalbPackagers(WPN);
  .print("Waiting packagers", WPN).