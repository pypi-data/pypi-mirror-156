# -*- coding: utf-8 -*-
import os
import sys
import six
import json
import tccli.options_define as OptionsDefine
import tccli.format_output as FormatOutput
from tccli import __version__
from tccli.utils import Utils
from tccli.exceptions import ConfigurationError, ParamError
from tencentcloud.common import credential
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.sqlserver.v20180328 import sqlserver_client as sqlserver_client_v20180328
from tencentcloud.sqlserver.v20180328 import models as models_v20180328


def doDescribeFlowStatus(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeFlowStatusRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeFlowStatus(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeOrders(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeOrdersRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeOrders(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeDBsNormal(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeDBsNormalRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeDBsNormal(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeDBCharsets(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeDBCharsetsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeDBCharsets(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeMigrationDetail(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeMigrationDetailRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeMigrationDetail(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeMigrations(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeMigrationsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeMigrations(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doRecycleDBInstance(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.RecycleDBInstanceRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.RecycleDBInstance(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyDBName(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyDBNameRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyDBName(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeIncrementalMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeIncrementalMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeIncrementalMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doInquiryPriceCreateDBInstances(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.InquiryPriceCreateDBInstancesRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.InquiryPriceCreateDBInstances(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doCloneDB(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.CloneDBRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.CloneDB(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyInstanceParam(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyInstanceParamRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyInstanceParam(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyDBInstanceProject(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyDBInstanceProjectRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyDBInstanceProject(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyDatabaseCT(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyDatabaseCTRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyDatabaseCT(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeSlowlogs(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeSlowlogsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeSlowlogs(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeBackups(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeBackupsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeBackups(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeZones(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeZonesRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeZones(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyBackupStrategy(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyBackupStrategyRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyBackupStrategy(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyAccountRemark(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyAccountRemarkRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyAccountRemark(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeUploadBackupInfo(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeUploadBackupInfoRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeUploadBackupInfo(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyAccountPrivilege(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyAccountPrivilegeRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyAccountPrivilege(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doRestartDBInstance(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.RestartDBInstanceRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.RestartDBInstance(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyDBInstanceName(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyDBInstanceNameRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyDBInstanceName(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doTerminateDBInstance(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.TerminateDBInstanceRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.TerminateDBInstance(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doCreateBackup(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.CreateBackupRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.CreateBackup(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doCreateDBInstances(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.CreateDBInstancesRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.CreateDBInstances(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doRollbackInstance(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.RollbackInstanceRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.RollbackInstance(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeDBs(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeDBsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeDBs(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeBackupMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeBackupMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeBackupMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doCreateBackupMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.CreateBackupMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.CreateBackupMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeDBInstances(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeDBInstancesRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeDBInstances(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyDatabaseMdf(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyDatabaseMdfRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyDatabaseMdf(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyDBRemark(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyDBRemarkRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyDBRemark(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDeleteIncrementalMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DeleteIncrementalMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DeleteIncrementalMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doCreateAccount(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.CreateAccountRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.CreateAccount(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doStartIncrementalMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.StartIncrementalMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.StartIncrementalMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doInquiryPriceUpgradeDBInstance(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.InquiryPriceUpgradeDBInstanceRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.InquiryPriceUpgradeDBInstance(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doResetAccountPassword(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ResetAccountPasswordRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ResetAccountPassword(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doCreateIncrementalMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.CreateIncrementalMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.CreateIncrementalMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doCreateMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.CreateMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.CreateMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeBackupUploadSize(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeBackupUploadSizeRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeBackupUploadSize(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeRegions(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeRegionsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeRegions(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDeleteMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DeleteMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DeleteMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyBackupMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyBackupMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyBackupMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doStartBackupMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.StartBackupMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.StartBackupMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyDBInstanceNetwork(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyDBInstanceNetworkRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyDBInstanceNetwork(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeBackupFiles(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeBackupFilesRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeBackupFiles(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeAccounts(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeAccountsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeAccounts(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyIncrementalMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyIncrementalMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyIncrementalMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeRollbackTime(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeRollbackTimeRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeRollbackTime(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDeleteDB(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DeleteDBRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DeleteDB(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doCreateDB(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.CreateDBRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.CreateDB(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDeleteAccount(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DeleteAccountRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DeleteAccount(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeInstanceParams(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeInstanceParamsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeInstanceParams(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeBackupCommand(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeBackupCommandRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeBackupCommand(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doRestoreInstance(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.RestoreInstanceRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.RestoreInstance(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeInstanceParamRecords(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeInstanceParamRecordsRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeInstanceParamRecords(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doUpgradeDBInstance(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.UpgradeDBInstanceRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.UpgradeDBInstance(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doRunMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.RunMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.RunMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDeleteBackupMigration(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DeleteBackupMigrationRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DeleteBackupMigration(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doDescribeProductConfig(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.DescribeProductConfigRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.DescribeProductConfig(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


def doModifyDatabaseCDC(args, parsed_globals):
    g_param = parse_global_arg(parsed_globals)

    cred = credential.Credential(
        g_param[OptionsDefine.SecretId], g_param[OptionsDefine.SecretKey], g_param[OptionsDefine.Token]
    )
    http_profile = HttpProfile(
        reqTimeout=60 if g_param[OptionsDefine.Timeout] is None else int(g_param[OptionsDefine.Timeout]),
        reqMethod="POST",
        endpoint=g_param[OptionsDefine.Endpoint]
    )
    profile = ClientProfile(httpProfile=http_profile, signMethod="HmacSHA256")
    mod = CLIENT_MAP[g_param[OptionsDefine.Version]]
    client = mod.SqlserverClient(cred, g_param[OptionsDefine.Region], profile)
    client._sdkVersion += ("_CLI_" + __version__)
    models = MODELS_MAP[g_param[OptionsDefine.Version]]
    model = models.ModifyDatabaseCDCRequest()
    model.from_json_string(json.dumps(args))
    rsp = client.ModifyDatabaseCDC(model)
    result = rsp.to_json_string()
    try:
        json_obj = json.loads(result)
    except TypeError as e:
        json_obj = json.loads(result.decode('utf-8'))  # python3.3
    FormatOutput.output("action", json_obj, g_param[OptionsDefine.Output], g_param[OptionsDefine.Filter])


CLIENT_MAP = {
    "v20180328": sqlserver_client_v20180328,

}

MODELS_MAP = {
    "v20180328": models_v20180328,

}

ACTION_MAP = {
    "DescribeFlowStatus": doDescribeFlowStatus,
    "ModifyMigration": doModifyMigration,
    "DescribeOrders": doDescribeOrders,
    "DescribeDBsNormal": doDescribeDBsNormal,
    "DescribeDBCharsets": doDescribeDBCharsets,
    "DescribeMigrationDetail": doDescribeMigrationDetail,
    "DescribeMigrations": doDescribeMigrations,
    "RecycleDBInstance": doRecycleDBInstance,
    "ModifyDBName": doModifyDBName,
    "DescribeIncrementalMigration": doDescribeIncrementalMigration,
    "InquiryPriceCreateDBInstances": doInquiryPriceCreateDBInstances,
    "CloneDB": doCloneDB,
    "ModifyInstanceParam": doModifyInstanceParam,
    "ModifyDBInstanceProject": doModifyDBInstanceProject,
    "ModifyDatabaseCT": doModifyDatabaseCT,
    "DescribeSlowlogs": doDescribeSlowlogs,
    "DescribeBackups": doDescribeBackups,
    "DescribeZones": doDescribeZones,
    "ModifyBackupStrategy": doModifyBackupStrategy,
    "ModifyAccountRemark": doModifyAccountRemark,
    "DescribeUploadBackupInfo": doDescribeUploadBackupInfo,
    "ModifyAccountPrivilege": doModifyAccountPrivilege,
    "RestartDBInstance": doRestartDBInstance,
    "ModifyDBInstanceName": doModifyDBInstanceName,
    "TerminateDBInstance": doTerminateDBInstance,
    "CreateBackup": doCreateBackup,
    "CreateDBInstances": doCreateDBInstances,
    "RollbackInstance": doRollbackInstance,
    "DescribeDBs": doDescribeDBs,
    "DescribeBackupMigration": doDescribeBackupMigration,
    "CreateBackupMigration": doCreateBackupMigration,
    "DescribeDBInstances": doDescribeDBInstances,
    "ModifyDatabaseMdf": doModifyDatabaseMdf,
    "ModifyDBRemark": doModifyDBRemark,
    "DeleteIncrementalMigration": doDeleteIncrementalMigration,
    "CreateAccount": doCreateAccount,
    "StartIncrementalMigration": doStartIncrementalMigration,
    "InquiryPriceUpgradeDBInstance": doInquiryPriceUpgradeDBInstance,
    "ResetAccountPassword": doResetAccountPassword,
    "CreateIncrementalMigration": doCreateIncrementalMigration,
    "CreateMigration": doCreateMigration,
    "DescribeBackupUploadSize": doDescribeBackupUploadSize,
    "DescribeRegions": doDescribeRegions,
    "DeleteMigration": doDeleteMigration,
    "ModifyBackupMigration": doModifyBackupMigration,
    "StartBackupMigration": doStartBackupMigration,
    "ModifyDBInstanceNetwork": doModifyDBInstanceNetwork,
    "DescribeBackupFiles": doDescribeBackupFiles,
    "DescribeAccounts": doDescribeAccounts,
    "ModifyIncrementalMigration": doModifyIncrementalMigration,
    "DescribeRollbackTime": doDescribeRollbackTime,
    "DeleteDB": doDeleteDB,
    "CreateDB": doCreateDB,
    "DeleteAccount": doDeleteAccount,
    "DescribeInstanceParams": doDescribeInstanceParams,
    "DescribeBackupCommand": doDescribeBackupCommand,
    "RestoreInstance": doRestoreInstance,
    "DescribeInstanceParamRecords": doDescribeInstanceParamRecords,
    "UpgradeDBInstance": doUpgradeDBInstance,
    "RunMigration": doRunMigration,
    "DeleteBackupMigration": doDeleteBackupMigration,
    "DescribeProductConfig": doDescribeProductConfig,
    "ModifyDatabaseCDC": doModifyDatabaseCDC,

}

AVAILABLE_VERSION_LIST = [
    "v20180328",

]


def action_caller():
    return ACTION_MAP


def parse_global_arg(parsed_globals):
    g_param = parsed_globals

    is_exist_profile = True
    if not parsed_globals["profile"]:
        is_exist_profile = False
        g_param["profile"] = "default"

    configure_path = os.path.join(os.path.expanduser("~"), ".tccli")
    is_conf_exist, conf_path = Utils.file_existed(configure_path, g_param["profile"] + ".configure")
    is_cred_exist, cred_path = Utils.file_existed(configure_path, g_param["profile"] + ".credential")

    conf = {}
    cred = {}

    if is_conf_exist:
        conf = Utils.load_json_msg(conf_path)
    if is_cred_exist:
        cred = Utils.load_json_msg(cred_path)

    if not (isinstance(conf, dict) and isinstance(cred, dict)):
        raise ConfigurationError(
            "file: %s or %s is not json format"
            % (g_param["profile"] + ".configure", g_param["profile"] + ".credential"))

    if OptionsDefine.Token not in cred:
        cred[OptionsDefine.Token] = None

    if not is_exist_profile:
        if os.environ.get(OptionsDefine.ENV_SECRET_ID) and os.environ.get(OptionsDefine.ENV_SECRET_KEY):
            cred[OptionsDefine.SecretId] = os.environ.get(OptionsDefine.ENV_SECRET_ID)
            cred[OptionsDefine.SecretKey] = os.environ.get(OptionsDefine.ENV_SECRET_KEY)
            cred[OptionsDefine.Token] = os.environ.get(OptionsDefine.ENV_TOKEN)

        if os.environ.get(OptionsDefine.ENV_REGION):
            conf[OptionsDefine.Region] = os.environ.get(OptionsDefine.ENV_REGION)

    for param in g_param.keys():
        if g_param[param] is None:
            if param in [OptionsDefine.SecretKey, OptionsDefine.SecretId, OptionsDefine.Token]:
                if param in cred:
                    g_param[param] = cred[param]
                else:
                    raise ConfigurationError("%s is invalid" % param)
            elif param in [OptionsDefine.Region, OptionsDefine.Output]:
                if param in conf:
                    g_param[param] = conf[param]
                else:
                    raise ConfigurationError("%s is invalid" % param)

    try:
        if g_param[OptionsDefine.ServiceVersion]:
            g_param[OptionsDefine.Version] = "v" + g_param[OptionsDefine.ServiceVersion].replace('-', '')
        else:
            version = conf["sqlserver"][OptionsDefine.Version]
            g_param[OptionsDefine.Version] = "v" + version.replace('-', '')

        if g_param[OptionsDefine.Endpoint] is None:
            g_param[OptionsDefine.Endpoint] = conf["sqlserver"][OptionsDefine.Endpoint]
    except Exception as err:
        raise ConfigurationError("config file:%s error, %s" % (conf_path, str(err)))

    if g_param[OptionsDefine.Version] not in AVAILABLE_VERSION_LIST:
        raise Exception("available versions: %s" % " ".join(AVAILABLE_VERSION_LIST))

    if six.PY2:
        for key, value in g_param.items():
            if isinstance(value, six.text_type):
                g_param[key] = value.encode('utf-8')
    return g_param

