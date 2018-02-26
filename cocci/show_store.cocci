@r@
declarer name DEVICE_ATTR_RO, DEVICE_ATTR_WO, DEVICE_ATTR_RW;
identifier attr =~ "attrname";
@@

(
 DEVICE_ATTR_RO (attr, ...);
|
 DEVICE_ATTR_WO (attr, ...);
|
 DEVICE_ATTR_RW (attr, ...);
)

@script:python p depends on r@
attr << r.attr;
ex_show;
ex_store;
@@

coccinelle.ex_show = attr + "_show"
coccinelle.ex_store = attr + "_store"

@e1@
identifier p.ex_show;
position p1;
identifier i;
@@

 ex_show@p1@i (...) { ... }

@script:python@
p1 << e1.p1;
show << p.ex_show;
@@

print ('show' + ' ' + show + ' ' + p1[0].line)

@e2@
identifier p.ex_store;
position p2;
@@

 ex_store@p2 (...) { ... }

@script:python@
p2 << e2.p2;
@@

print ('store ' + p2[0].line)

@ra@
declarer name DEVICE_ATTR;
identifier attr =~ "attrname";
identifier show, store;
@@

 DEVICE_ATTR (attr, ..., show, store);

@r1 depends on ra@
position p3;
identifier ra.show;
@@

 show@p3 (...) { ... }

@script:python@
p3 << r1.p3;
show << ra.show;
@@

print ('show' + ' ' + show + ' ' + p3[0].line)

@r2 depends on ra@
identifier ra.store;
position p4;
@@

 store@p4 (...) { ... }

@script:python@
p4 << r2.p4;
@@

print ('store ' + p4[0].line)

