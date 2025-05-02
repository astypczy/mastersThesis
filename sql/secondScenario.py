
# CREATE TABLE big_table (
#   id SERIAL PRIMARY KEY,
#   col1 VARCHAR(50),
#   col2 VARCHAR(50),
#   -- ... (ciąg dalszy do 1000 kolumn) ...
#   col1000 VARCHAR(50)
# );

with open("outputFlyway.txt", "w") as f:
    f.write("CREATE TABLE big_table (\n")
    f.write("\tid SERIAL PRIMARY KEY,\n")
    for i in range(1,1000):
        f.write("\tcol"+str(i)+ " VARCHAR(50),\n")
    f.write("\tcol1000 VARCHAR(50)\n")
    f.write(");\n")

# <changeSet id="create-big-table" author="demo">
#   <createTable tableName="big_table">
#     <column name="id" type="SERIAL">
#       <constraints primaryKey="true"/>
#     </column>
#     <column name="col1" type="VARCHAR(50)"/>
#     <column name="col2" type="VARCHAR(50)"/>
#     <!-- ... -->
#     <column name="col1000" type="VARCHAR(50)"/>
#   </createTable>
# </changeSet>

with open("outputLiquibase.txt", "w") as f:
    f.write("<changeSet id=\"create-big-table\" author=\"dev\">\n")
    f.write("  <createTable tableName=\"big_table\">\n")
    f.write("    <column name=\"id\" type=\"SERIAL\">\n")
    f.write("      <constraints primaryKey=\"true\"/>\n")
    f.write("    </column>\n")
    for i in range(1,1000):
        f.write("    <column name=\"col"+str(i)+"\" type=\"VARCHAR(50)\"/>\n")
    f.write("    <column name=\"col1000\" type=\"VARCHAR(50)\"/>\n")
    f.write("  </createTable>\n")
    f.write("</changeSet>\n")