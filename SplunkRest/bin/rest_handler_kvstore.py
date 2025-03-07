#!/usr/bin/env python
# coding=utf-8

__name__ = "trackme_rest_handler_ack.py"
__author__ = "TrackMe Limited"
__copyright__ = "Copyright 2023-2024, TrackMe Limited, U.K."
__credits__ = "TrackMe Limited, U.K."
__license__ = "TrackMe Limited, all rights reserved"
__version__ = "0.1.0"
__maintainer__ = "TrackMe Limited, U.K."
__email__ = "support@trackme-solutions.com"
__status__ = "PRODUCTION"

# Built-in libraries
import json
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

# splunk home
splunkhome = os.environ["SPLUNK_HOME"]

# set logging
logger = logging.getLogger(__name__)
filehandler = RotatingFileHandler(
    "%s/var/log/splunk/trackme_rest_api.log" % splunkhome,
    mode="a",
    maxBytes=10000000,
    backupCount=1,
)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(filename)s %(funcName)s %(lineno)d %(message)s"
)
logging.Formatter.converter = time.gmtime
filehandler.setFormatter(formatter)
log = logging.getLogger()
for hdlr in log.handlers[:]:
    if isinstance(hdlr, logging.FileHandler):
        log.removeHandler(hdlr)
log.addHandler(filehandler)
log.setLevel(logging.INFO)

# append libs
sys.path.append(os.path.join(splunkhome, "etc", "apps", "trackme", "lib"))

# import rest handler
import trackme_rest_handler

# import trackme libs
from trackme_libs import (
    trackme_getloglevel,
    trackme_audit_event,
)

from trackme_libs_ack import (
    get_all_ack_records_from_kvcollection,
    convert_epoch_to_datetime,
)

# import Splunk libs
import splunklib.client as client


class TrackMeHandlerAck_v2(trackme_rest_handler.RESTHandler):
    def __init__(self, command_line, command_arg):
        super(TrackMeHandlerAck_v2, self).__init__(command_line, command_arg, logger)

    def get_resource_group_desc_ack(self, request_info, **kwargs):
        response = {
            "resource_group_name": "ack",
            "resource_group_desc": "Acknowledgments allow silencing an entity alert for a given period of time automatically",
        }

        return {"payload": response, "status": 200}

    def post_ack_manage(self, request_info, **kwargs):

        describe = False
        tenant_id = None

        # Retrieve from data
        try:
            resp_dict = json.loads(str(request_info.raw_args["payload"]))
        except Exception as e:
            resp_dict = None

        if resp_dict is not None:
            try:
                describe = resp_dict["describe"]
                if describe in ("true", "True"):
                    describe = True
            except Exception as e:
                describe = False
            if not describe:
                # tenant_id is required
                tenant_id = resp_dict.get("tenant_id", None)
                if tenant_id is None:
                    error_msg = f'tenant_id="{tenant_id}", tenant_id is required'
                    logging.error(error_msg)
                    return {
                        "payload": {"action": "failure", "result": error_msg},
                        "status": 500,
                    }

                # the action, if not specified, show will be the default
                action = resp_dict.get("action", "show")
                if action not in ("show", "enable", "disable"):
                    # log error and return
                    error_msg = f'tenant_id="{tenant_id}", action="{action}", action is incorrect, valid options are show | enable | disable'
                    logging.error(error_msg)
                    return {
                        "payload": {"action": "failure", "result": error_msg},
                        "status": 500,
                    }

                # object_list
                object_list = resp_dict.get("object_list", None)
                object_value_list = []

                # for action = show, if not set, will be defined to *
                # for action = enable/disable, if not set, will return an error

                if object_list is None:
                    if action == "show":
                        object_list = "*"
                    else:
                        error_msg = f'tenant_id="{tenant_id}", action="{action}", object_list is required'
                        logging.error(error_msg)
                        return {
                            "payload": {"action": "failure", "result": error_msg},
                            "status": 500,
                        }

                else:
                    # turn as a list
                    object_value_list = object_list.split(",")

                # object_category
                object_category_value = resp_dict["object_category"]

                # ack_period
                ack_period = resp_dict.get("ack_period", 86400)
                try:
                    ack_period = int(ack_period)
                except Exception as e:
                    # log error format and return error
                    error_msg = f'tenant_id="{tenant_id}", ack_period="{ack_period}", ack_period period is incorrect, an integer is expected, exception="{str(e)}"'
                    logging.error(error_msg)
                    return {
                        "payload": {"action": "failure", "result": error_msg},
                        "status": 500,
                    }

                # ack_type is optional, if not set, will be defined to unsticky
                ack_type = resp_dict.get("ack_type", "unsticky")
                if not ack_type in ("sticky", "unsticky"):
                    # log error format and return error
                    error_msg = f'tenant_id="{tenant_id}", ack_type="{ack_type}", ack_type is incorrect, valid options are sticky | unsticky'
                    logging.error(error_msg)
                    return {
                        "payload": {"action": "failure", "result": error_msg},
                        "status": 500,
                    }

                # ack_comment
                ack_comment = resp_dict.get("ack_comment", None)

                # anomaly_reason is optional, if not set, will be defined to N/A
                anomaly_reason = resp_dict.get("anomaly_reason", "N/A")

                # ack_source is optional, if not set, will be defined to user_ack
                ack_source = resp_dict.get("ack_source", "user_ack")

                if not ack_source in ("auto_ack", "user_ack"):
                    # log error format and return error
                    error_msg = f'tenant_id="{tenant_id}", ack_source="{ack_source}", ack_source is incorrect, valid options are auto_ack | user_ack'
                    logging.error(error_msg)
                    return {
                        "payload": {"action": "failure", "result": error_msg},
                        "status": 500,
                    }

        else:
            # body is required in this endpoint, if not submitted describe the usage
            describe = True

        if describe:
            response = {
                "describe": "This endpoint will enable/disable an acknowledgment for one or more entities, it requires a POST call with the following information:",
                "resource_desc": "Show/Enable/Disable/Update acknowledgement for a comma separated list of entities",
                "resource_spl_example": '| trackme url="/services/trackme/v2/ack/ack_manage" mode="post" body="{\'tenant_id\': \'mytenant\', '
                + "'action': 'enable', 'object_category': 'splk-dsm', 'object_list': 'netscreen:netscreen:firewall', 'ack_period': 86400, 'ack_comment': 'Under review'}\"",
                "options": [
                    {
                        "tenant_id": "The tenant identifier",
                        "action": "The action to be performed, valid options are: enable | disable | show.",
                        "object_category": "the object category (splk-dsm, splk-dhm, splk-mhm, splk-cim, splk-flx, splk-wlk)",
                        "object_list": "List of entities, in a comma separated format. If action=show and not set, will be defined to * to retrieve all Ack records, mandatory for action=enable/disable",
                        "ack_period": "Required if action=enable, the period for the acknowledgment in seconds",
                        "ack_type": "The type of Ack, valid options are sticky | unsticky, defaults to unsticky if not specified. Unsticky Ack are purged automatically when the entity goes back to a green state, while sticky Ack are purged only when the expiration is reached.",
                        "ack_comment": "Relevant if action=enable but optional, the acknowlegment comment to be added to the records",
                        "ack_source": "OPTIONAL: the source of the ack, if unset will be defined to: user_ack. Valid options are: auto_ack, user_ack",
                        "anomaly_reason": "OPTIONAL: the reason for the anomaly, if unset will be defined to: N/A",
                        "update_comment": "OPTIONAL: a comment for the update, comments are added to the audit record, if unset will be defined to: API update",
                    }
                ],
            }
            return {"payload": response, "status": 200}

        # Update comment is optional and used for audit changes
        try:
            update_comment = resp_dict["update_comment"]
        except Exception as e:
            update_comment = "API update"

        # ack_comment
        if ack_comment is None:
            ack_comment = update_comment

        # counters
        processed_count = 0
        succcess_count = 0
        failures_count = 0

        # records summary
        records_summary = []

        # Get splunkd port
        splunkd_port = request_info.server_rest_port

        # Get service
        service = client.connect(
            owner="nobody",
            app="trackme",
            port=splunkd_port,
            token=request_info.session_key,
            timeout=300,
        )

        # set loglevel
        loglevel = trackme_getloglevel(
            request_info.system_authtoken, request_info.server_rest_port
        )
        log.setLevel(logging.getLevelName(loglevel))

        collection_name = f"kv_trackme_common_alerts_ack_tenant_{tenant_id}"
        collection = service.kvstore[collection_name]

        # Component mapping
        component_mapping = {
            "splk-dsm": "dsm",
            "splk-dhm": "dhm",
            "splk-mhm": "mhm",
            "splk-flx": "flx",
            "splk-cim": "cim",
            "splk-wlk": "wlk",
        }

        # get the whole collection
        try:
            (
                collection_records_list,
                collection_records_keys,
                collection_records_objects,
                collection_records_objects_dict,
                collection_records_keys_dict,
            ) = get_all_ack_records_from_kvcollection(
                collection_name, collection, object_category_value
            )

        except Exception as e:
            error_msg = f'tenant_id="{tenant_id}", failed to retrieve KVstore collection records using function get_all_records_from_kvcollection, exception="{str(e)}"'
            logging.error(error_msg)
            return {
                "payload": {"action": "failure", "result": error_msg},
                "status": 500,
            }

        # if action is show and object_list is *, return all records
        if action == "show" and object_list == "*":
            return {
                "payload": {
                    "process_count": len(collection_records_list),
                    "records": collection_records_list,
                },
                "status": 200,
            }

        else:
            # action show
            if action == "show":
                for object_value in object_value_list:
                    if object_value in collection_records_objects:
                        # increment counter
                        processed_count += 1
                        succcess_count += 1
                        failures_count += 0

                        records_summary.append(
                            collection_records_objects_dict[object_value]
                        )

                    else:
                        # increment counter
                        processed_count += 1
                        succcess_count += 0
                        failures_count += 1

                        result = {
                            "object": object_value,
                            "action": "show",
                            "result": "failure",
                            "exception": f'tenant_id="{tenant_id}", the entity="{object_value}" could not be found in this tenant',
                        }
                        records_summary.append(result)

            # action enable
            elif action == "enable" or action == "disable":
                if action == "enable":
                    ack_state = "active"
                    ack_expiration = time.time() + ack_period
                else:
                    ack_state = "inactive"
                    ack_expiration = 0
                    ack_type = "N/A"

                for object_value in object_value_list:

                    ack_record = {
                        "object": object_value,
                        "object_category": object_category_value,
                        "anomaly_reason": anomaly_reason,
                        "ack_source": ack_source,
                        "ack_expiration": ack_expiration,
                        "ack_state": ack_state,
                        "ack_mtime": time.time(),
                        "ack_type": ack_type,
                        "ack_comment": ack_comment,
                    }

                    # only for enable, on a per object and if anomaly_reason is not set
                    if action == "enable":
                        # if action is enable, and anomaly_reason is not set, attempt to connect to the data KV and retrieve the actual anomaly_reason
                        if anomaly_reason == "N/A":

                            try:
                                collection_data_name = f"kv_trackme_{component_mapping.get(object_category_value, None)}_tenant_{tenant_id}"
                                collection_data = service.kvstore[collection_data_name]
                                data_kvrecord = collection_data.data.query(
                                    query=json.dumps({"object": object_value})
                                )[0]
                                ack_record["anomaly_reason"] = data_kvrecord.get(
                                    "anomaly_reason", "N/A"
                                )

                            except Exception as e:
                                error_msg = f'tenant_id="{tenant_id}", while attempting to retrieve the anomaly_reason in the data KVstore {collection_data_name} an exception was encountered, exception="{str(e)}"'
                                logging.error(error_msg)

                    try:
                        if object_value in collection_records_objects:
                            # Update the record
                            collection.data.update(
                                collection_records_objects_dict[object_value]["_key"],
                                json.dumps(ack_record),
                            )
                        else:
                            collection.data.insert(json.dumps(ack_record))

                        # increment counter
                        processed_count += 1
                        succcess_count += 1
                        failures_count += 0

                        result = {
                            "object": object_value,
                            "action": action,
                            "result": "success",
                            "ack_record": ack_record,
                        }
                        records_summary.append(result)

                        # set audit message depending on the action (enable / disable)
                        if action == "enable":
                            audit_msg = "The Ack was enabled successfully"
                        elif action == "disable":
                            audit_msg = "The Ack was disabled successfully"

                        # audit
                        trackme_audit_event(
                            request_info.system_authtoken,
                            request_info.server_rest_uri,
                            tenant_id,
                            request_info.user,
                            "success",
                            f"{action} ack",
                            str(object_value),
                            str(object_category_value),
                            ack_record,
                            audit_msg,
                            str(update_comment),
                        )

                    except Exception as e:
                        # increment counter
                        processed_count += 1
                        succcess_count += 0
                        failures_count += 1

                        result = {
                            "object": object_value,
                            "action": "enable",
                            "result": "failure",
                            "exception": f'tenant_id="{tenant_id}", the entity="{object_value}" could not be updated, exception="{str(e)}"',
                        }
                        records_summary.append(result)

                        # set audit message depending on the action (enable / disable)
                        if action == "enable":
                            audit_msg = (
                                f"The Ack could not be enabled, exception={str(e)}"
                            )
                        elif action == "disable":
                            audit_msg = (
                                f"The Ack could not be disabled, exception={str(e)}"
                            )

                        # audit
                        trackme_audit_event(
                            request_info.system_authtoken,
                            request_info.server_rest_uri,
                            tenant_id,
                            request_info.user,
                            "failure",
                            f"{action} ack",
                            str(object_value),
                            str(object_category_value),
                            ack_record,
                            audit_msg,
                            str(update_comment),
                        )

            # render HTTP status and summary
            req_summary = {
                "process_count": processed_count,
                "success_count": succcess_count,
                "failures_count": failures_count,
                "records": records_summary,
            }

            if processed_count > 0 and processed_count == succcess_count:
                http_status = 200
            else:
                http_status = 500

            return {"payload": req_summary, "status": http_status}

    def post_get_ack_for_object(self, request_info, **kwargs):

        describe = False
        tenant_id = None

        # Retrieve from data
        try:
            resp_dict = json.loads(str(request_info.raw_args["payload"]))
        except Exception as e:
            resp_dict = None

        if resp_dict is not None:
            try:
                describe = resp_dict["describe"]
                if describe in ("true", "True"):
                    describe = True
            except Exception as e:
                describe = False
            if not describe:
                # tenant_id is required
                tenant_id = resp_dict.get("tenant_id", None)
                if tenant_id is None:
                    error_msg = f'tenant_id="{tenant_id}", tenant_id is required'
                    logging.error(error_msg)
                    return {
                        "payload": {"action": "failure", "result": error_msg},
                        "status": 500,
                    }

                # object_list
                object_list = resp_dict.get("object_list", None)
                object_value_list = []

                if object_list is None:
                    object_list = "*"

                else:
                    # turn as a list
                    object_value_list = object_list.split(",")

                # object_category
                object_category_value = resp_dict["object_category"]

        else:
            # body is required in this endpoint, if not submitted describe the usage
            describe = True

        if describe:
            response = {
                "describe": "This endpooint retrieves the Ack record for one or more objects, it requires a POST call with the following information:",
                "resource_desc": "Get acknowledgement for a comma separated list of entities",
                "resource_spl_example": "| trackme url=\"/services/trackme/v2/ack/get_ack_for_object\" mode=\"post\" body=\"{'tenant_id': 'mytenant', 'object_category': 'splk-dsm', 'object_list': 'netscreen:netscreen:firewall'}\"",
                "options": [
                    {
                        "tenant_id": "The tenant identifier",
                        "object_category": "the object category (splk-dsm, splk-dhm, splk-mhm, splk-cim, splk-flx, splk-wlk)",
                        "object_list": "List of entities, in a comma separated format. Use * to retrieve all objects, defaults to * if not specified",
                    }
                ],
            }
            return {"payload": response, "status": 200}

        # Get splunkd port
        splunkd_port = request_info.server_rest_port

        # Get service
        service = client.connect(
            owner="nobody",
            app="trackme",
            port=splunkd_port,
            token=request_info.session_key,
            timeout=300,
        )

        # set loglevel
        loglevel = trackme_getloglevel(
            request_info.system_authtoken, request_info.server_rest_port
        )
        log.setLevel(logging.getLevelName(loglevel))

        collection_name = f"kv_trackme_common_alerts_ack_tenant_{tenant_id}"
        collection = service.kvstore[collection_name]

        # get the whole collection
        try:
            (
                collection_records_list,
                collection_records_keys,
                collection_records_objects,
                collection_records_objects_dict,
                collection_records_keys_dict,
            ) = get_all_ack_records_from_kvcollection(
                collection_name, collection, object_category_value
            )

        except Exception as e:
            error_msg = f'tenant_id="{tenant_id}", failed to retrieve KVstore collection records using function get_all_records_from_kvcollection, exception="{str(e)}"'
            logging.error(error_msg)
            return {
                "payload": {"action": "failure", "result": error_msg},
                "status": 500,
            }

        # if action is show and object_list is *, return all records
        filtered_records = []

        if object_list == "*":
            for record in collection_records_list:
                # convert ack_mtime to ack_mtime_datetime
                ack_mtime_datetime = convert_epoch_to_datetime(record.get("ack_mtime"))
                record["ack_mtime_datetime"] = ack_mtime_datetime

                # convert ack_expiration to ack_expiration_datetime
                ack_expiration_datetime = convert_epoch_to_datetime(
                    record.get("ack_expiration")
                )
                record["ack_expiration_datetime"] = ack_expiration_datetime

                # create a new field called ack_is_enabled which is a boolean 0/1 depending on if the ack_state is active or inactive
                if record.get("ack_state") == "active":
                    record["ack_is_enabled"] = 1
                else:
                    record["ack_is_enabled"] = 0

                # field anomaly_reason is optional, if not set, will be defined to N/A, if set it is a comma seperated string to be turned into a list
                anomaly_reason = record.get("anomaly_reason", None)
                if not anomaly_reason:
                    record["anomaly_reason"] = "N/A"
                else:
                    if not isinstance(anomaly_reason, list):
                        record["anomaly_reason"] = anomaly_reason.split(",")

                # field ack_source is optional, if not set, will be defined to user_ack
                ack_source = record.get("ack_source", "user_ack")
                record["ack_source"] = ack_source

                filtered_records.append(record)

            return {
                "payload": filtered_records,
                "status": 200,
            }

        else:
            filtered_records = []
            for object_value in object_value_list:
                if object_value in collection_records_objects:
                    record = collection_records_objects_dict[object_value]

                    # convert ack_mtime to ack_mtime_datetime
                    ack_mtime_datetime = convert_epoch_to_datetime(
                        record.get("ack_mtime")
                    )
                    record["ack_mtime_datetime"] = ack_mtime_datetime

                    # convert ack_expiration to ack_expiration_datetime
                    if record.get("ack_expiration") != 0:
                        ack_expiration_datetime = convert_epoch_to_datetime(
                            record.get("ack_expiration")
                        )
                    else:
                        ack_expiration_datetime = "N/A"
                    record["ack_expiration_datetime"] = ack_expiration_datetime

                    # create a new field called ack_is_enabled which is a boolean 0/1 depending on if the ack_state is active or inactive
                    if record.get("ack_state") == "active":
                        record["ack_is_enabled"] = 1
                    else:
                        record["ack_is_enabled"] = 0

                    # field anomaly_reason is optional, if not set, will be defined to N/A, if set it is a comma seperated string to be turned into a list
                    anomaly_reason = record.get("anomaly_reason", None)
                    if not anomaly_reason:
                        record["anomaly_reason"] = "N/A"
                    else:
                        if not isinstance(anomaly_reason, list):
                            record["anomaly_reason"] = anomaly_reason.split(",")

                    # field ack_source is optional, if not set, will be defined to user_ack
                    ack_source = record.get("ack_source", "user_ack")
                    record["ack_source"] = ack_source

                    filtered_records.append(record)

            return {
                "payload": filtered_records,
                "status": 200,
            }
