/routing rule remove [find table="unicom" and comment!="STATIC-MARK-MAPPING"];
/routing rule add dst-address=2001:252::/32 action=lookup table="unicom";
/routing rule add dst-address=2001:7fa:5::/48 action=lookup table="unicom";