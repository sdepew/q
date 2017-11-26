from bot.command_map import command_map
import boto3
import botocore
import os
import logging

logger = logging.getLogger()

# These are the allowed Keys
remember_options = ["music", "weather"]


def create_table(table_name=""):
    # TODO Figure out what I want to check here if this is different.
    if table_name != os.environ['REMEMBER_DDB_TABLE']:
        try:
            logger.debug("Creating Table {}".format(table_name))
            dynamodb = connect_dynamo(region='us-east-1')
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'name',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'command',
                        'KeyType': 'RANGE'  # Sort key
                    },
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'name',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'command',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            os.environ['REMEMBER_DDB_TABLE'] = table.name
        except dynamodb.ResourceInUseException:
            return True
        else:
            return True
    else:
        return False


def connect_dynamo(region='us-east-1'):
    return boto3.resource('dynamodb', region_name=region)


def use_table():
    dynamodb = connect_dynamo(region='us-east-1')
    return dynamodb.Table(os.environ['REMEMBER_DDB_TABLE'])


def put_item_dynamo(query={}, user=""):
    '''
    :param query: list
    :param name: string
    :return: dict of updated items {'command': 'preference'}
    '''
    answers = {}
    table = use_table()
    try:
        for command, preference in query.items():
            if command.lower() in remember_options:
                response = table.update_item(
                    Key={
                        'name': user,
                        'command': command
                    },
                    UpdateExpression="set preference = :k",
                    ExpressionAttributeValues={
                        ':k': preference
                    },
                    ReturnValues="UPDATED_NEW"
                )
                answers[command] = response['Attributes']['preference']
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            create_table(os.environ['REMEMBER_DDB_TABLE'])
            table.wait_until_exists()
            put_item_dynamo(query=query, name=user)
    else:
        return answers


def read_from_dynamodb(query=[], user=""):
    user_input = dict(i.split(':') for i in query)
    table = use_table()
    commands = {}
    for command, preference in user_input.items():
        response = table.get_item(
            Key={
                'name': user,
                'command': command
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            try:
                logger.debug("Item found in Dynamo:\n"
                             "User: {}\n"
                             "Command: {}\n"
                             "Preference: {}\n".format(
                                                        response['Item']['name'],
                                                        response['Item']['command'],
                                                        response['Item']['preference']))
                commands[response['Item']['command']] = response['Item']['preference']
            except botocore.exceptions.ClientError as read_e:
                logger.error("Couldnt find {} for {}: {}".format(command, user, read_e))
                continue
            except KeyError as key_error:
                logger.debug('Unable to find command {} for {} in Dynamo.'.format(command, user))
                continue
    return commands


def valid_option(query):
    user_input = dict(i.split(':') for i in query)
    valid_dict = dict(i for i in user_input.items() if i[0] in remember_options)
    return valid_dict


@command_map.register_command()
def remember(query=[], user=""):
    '''
    Have me remember command preferences for you.
    --------------------------------------------------------
    *Usage:*
    `!remember music:google weather:20170`
    Each `command:preference` set *MUST* be set in the format indicated.
    --------------------------------------------------------
    '''
    logger.debug("Trying to update user preferences.\nUser: {}, Query {}".format(user, query))
    user_input = valid_option(query)
    if query and user_input:
        # Update Entries and return entries.
        response = "I'm awesome! I updated these:\n"
        try:
            updated_items = put_item_dynamo(user_input, user)
            if updated_items:
                for command, preference in updated_items.items():
                    response += "*{}*: {}".format(command, preference)
            else:
                response = "Yeah, I couldn't update those, come back after the Olympics."
        except Exception as e:
            logger.error("Error when updating user preferences: {}".format(e))
    else:
        # Return Error that we dont allow those.
        logger.warning("Query entered did not match any entries in list remember_options")
        return "You sure about that? I don't recognize those options."
    return response
