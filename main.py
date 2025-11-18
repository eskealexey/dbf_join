from lib import json_to_dbf_corrected, dbf_to_json, smart_json_merge

# Использование
dbf_to_json('file1.dbf', 'output1.json')
dbf_to_json('file2.dbf', 'output2.json')
smart_json_merge('output1.json', 'output2.json', 'final_merged.json')

field_defs = "LC:C:6,FM:C:23,IM:C:21,OT:C:21,REM:C:10,GOD:C:4,N:C:2,KOD_OTKR:C:4,DAT_OTKR:D,KOD_ZAKR:C:11,DAT_ZAKR:D,DATR:D,VPEN:C:3,SNAZN:N:10:2,D_YXOD:D,D_DESTR:D,VPN:C:3,CART:C:2,DNASN:D"  # Поле ID, текст, длина 10

json_to_dbf_corrected('final_merged.json', 'output.dbf', field_defs)