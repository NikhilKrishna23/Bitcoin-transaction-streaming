
## Real-time Bitcoin Transaction Streaming and Analysis Platform



## Instructions:
1. Download Kafka from the drive link: https://drive.google.com/open?id=1J5_C-qkE7Ci4es1RvkAikSCATFx27huh
**Note**: This version is the version with my configurations.

1. Download the three py files and the requirements.txt file.

1. Extract the zip file and move into the directory: kafka_2.12-2.3.0/bin/

1. Start the zookeeper server and kafka server by executing the following command in two different terminals:

    1. $./zookeeper-server-start.sh ../config/zookeeper.properties
    1. $./kafka-server-start.sh ../config/server.properties
   
1. Ensure that redis server is running (port=6379).

1. Execute the following command to install the dependencies:

    1. $ pip3 install -r requirements.txt
  
1. Run the following commands inside kafka_2.12-2.3.0/bin directory to ensure that the topic and retention time is set properly:
  
    1. $ ./kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic bchain
    1. $ ./kafka-configs.sh --zookeeper localhost:2181 --alter --entity-type topics --entity-name bchain --add-config 'retention.ms=10800000'
 
1. Run the three python codes parallely in the order:
    1.producer.py
    1.consumer.py
    1.api.py

1. Once the python codes are up and running, try accessing the following endpoints in your browser:
    1. http://localhost:8000/show_transactions
    1. http://localhost:8000/transactions_count_per_minute/?min_value=15:53/   **NOTE: Replace *15:53* with the desired minute value in 24 hr format.**
    1. http://localhost:8000/high_value_addr
  
## Information:
1. Screenshots folder contains screenshot of the output of the three endpoints.

1. Kafka retention time is set to 10800000ms in order to persist only the transactions made in the last 3 hours.

1. Retention time has been set as 3hrs in redis for the addresses that are saved and used for computing the address with high aggregate transactions.

1. Retention time has been set as 1hr in redis for the transaction count in last one hour.

1. Ensure that the minute value entered is within the timeframe i.e For example, if the program was started at 18:00 and the endpoint is accessed at 18:50, ensure that the minute entered is within 18:00 - 18:50.

1. The following algorithm was used for calculation the aggregate transactions:
    1. If the spent flag is set as True for the output address, the address is stored in the database and no change is made to the net transaction value i.e O is the increment value.
    1. If the spent flag is set as False for the output address, it is considered as UTXO; the address is stored in the database and the net transaction value is incremented by the respective value.
    1. The address specified in the input is stored in the database and the net transaction value is decremented  by the respective value. **NOTE:** The spent flag is not checked for inputs because the spent flag is automatically changed to true in the blockchain UTXO blocks when a transaction is initiated.
    
