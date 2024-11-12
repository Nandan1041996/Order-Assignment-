# Order-Assignment-
--> objective : To automate placement of order to perticular customer available in pending order file and according to that make changes in stock file where plant wise stock is given.

--> User Input copntains : 1) pending order file : pending orders of customer, 2) rate file : from plant what is the charges to send material to customer , 3) stock file contains stock availability in perticular plant 

--> File format and Columns:
   All file format should be xlsx. or xls.
  1) Pending Order File : File must contain the following columns:
    'Plant', 'Sales Order', 'Material No.', 'Sold to', 'Ship to Party Name','Sch Open Qty.', 'UoM', 'Disp. Date', 'Trp Zone', 'Destination', 'Incoterms'
  2) Rate File : File must contain the following columns:
    'Plant', 'Plant Zone', 'Plant Zone Desc'. 'CFS Source', 'CFS Destination','Final Destination', 'Dest. Desc.', Route Name', 'MODE','Total with STO'
  3) Stock File : File must contain the following columns:
    'Palnt', 'Material', 'Total Stock(Desp+Tra'
--> When User click on submit button all calculation in backend perform and we get Unique Order number, User can select all the order number to see or specific orders to see       that Order is placed or not and user can download file as well.
