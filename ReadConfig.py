import boto3
import logging
import sys
import requests
import pandas
import pyarrow
import pyarrow.parquet as pq
import s3fs


aws_s3_fs = s3fs.S3FileSystem()
sess = boto3.session.Session()
region = sess.region_name
s3 = boto3.resource('s3')


config_list = []
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOG_GROUP_NAME = None
LOG_STREAM_NAME = None

CONFIG_BUCKET_NAME = 'open-business-datamart'
DESTINATION_BUCKET_NAME = 'gluedatadiscovery-raws3bucket-ocucokzux6nx'

def error_handler(error, fail=True):
    try:
        LOGGER.error('The following error has occurred on line: %s')
        LOGGER.error(str(error))

        message = "https://{0}.console.aws.amazon.com/cloudwatch/home?region={0}#logEventViewer:group={1};stream={2}".format(
            region, LOG_GROUP_NAME, LOG_STREAM_NAME)
        LOGGER.error(message)
        if fail:
            sys.exit(1)

    except Exception as err:
        LOGGER.error(
            'The following error has occurred on line: %s',
            sys.exc_info()[2].tb_lineno)
        LOGGER.error(str(err))
        sys.exit(1)





def get_datasources_froms3(bucketname, objectname):
    try:
        s3 = boto3.resource('s3')
        config_file = s3.Object(bucketname, objectname)

        for line in config_file.get()['Body']._raw_stream:
            #print(line)
            line = line.strip()
            if(len(line) == 0):
                continue
            config_dict = {}
            for items in line.decode().split(','):
                pair = items.split('=')
                #print(pair)
                config_dict[pair[0].strip()] = pair[1].strip()

            config_list.append(config_dict)
    except Exception as e:
        print(e)
        error_handler(e)



def get_datasources(configlocation):
    """
    :param configlocation: is the path of the data sources config file
    :return: dictionary object of source urls
    """
    try:
        with open(configlocation,'r') as stream:
            print(stream.readline())

    except Exception as e:
        print(e)



def fetch_datasources_list():
    print('Reading Config')
    get_datasources_froms3(CONFIG_BUCKET_NAME, 'ConfigDataSources.txt')
    #print(config_list)


def read_datasource(item):
    #print(config_list)
    print(f'Reading data from data source {config_list[item].get("Name")}')
    name = config_list[item].get("Name")
    print('Type is {} and Location {}'.format(config_list[item].get("Type"), config_list[item].get("location")))

    if(config_list[item].get("Type").lower() == 'csv'):
        """r = requests.get(config_list[item].get("location"), stream=True)
        linecount = 0
        for line in r.iter_lines():
            if line:
                if linecount == 0:
                    print ('Header - Columns : ', line)
                else:
                    print(line)
                linecount += 1
        print('Number of rows {}'.format(linecount))
        """
        dataframe = pandas.read_csv(config_list[item].get("location"), sep=',', quotechar='"', encoding='utf8')
        #dataframe.to_parquet(config_list[item].get("Name"), engine='auto', compression='snappy')
        #table = pyarrow.Table.from_pandas(dataframe)
        output_file = f"s3://{DESTINATION_BUCKET_NAME}/{name}.parquet"
        try:
            aws_s3_fs.ls(DESTINATION_BUCKET_NAME)
        except:
            #s3.create_bucket(Bucket=DESTINATION_BUCKET_NAME, CreateBucketConfiguration=dict(LocationConstraint='eu-west-2'))
            aws_s3_fs.mkdir(DESTINATION_BUCKET_NAME)
            print('Created Bucket')
        else:
            dataframe.to_parquet(output_file, engine='auto', compression='snappy')
            print('Bucket exists and file created', output_file)
            #pq.write_to_dataset(table=name, root_path=output_file, filesystem=aws_s3_fs)




def read_datasources():
    fetch_datasources_list()
    for src_num in range(len(config_list)):
        read_datasource(src_num)


read_datasources()
