# -*- coding: utf8 -*-
# Copyright (c) 2017-2021 THL A29 Limited, a Tencent company. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.abstract_client import AbstractClient
from tencentcloud.redis.v20180412 import models


class RedisClient(AbstractClient):
    _apiVersion = '2018-04-12'
    _endpoint = 'redis.tencentcloudapi.com'
    _service = 'redis'


    def AllocateWanAddress(self, request):
        """This API is used to enable public network access.

        :param request: Request instance for AllocateWanAddress.
        :type request: :class:`tencentcloud.redis.v20180412.models.AllocateWanAddressRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.AllocateWanAddressResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("AllocateWanAddress", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.AllocateWanAddressResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def ChangeReplicaToMaster(self, request):
        """This API is used to promote a replica node group of a multi-AZ deployed instance to master node group or a replica node of a single-AZ deployed instance to master node.

        :param request: Request instance for ChangeReplicaToMaster.
        :type request: :class:`tencentcloud.redis.v20180412.models.ChangeReplicaToMasterRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.ChangeReplicaToMasterResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("ChangeReplicaToMaster", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.ChangeReplicaToMasterResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceAccount(self, request):
        """This API is used to view instance sub-account information.

        :param request: Request instance for DescribeInstanceAccount.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceAccountRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceAccountResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceAccount", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceAccountResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceMonitorBigKey(self, request):
        """This API is used to query the big key of an instance.

        :param request: Request instance for DescribeInstanceMonitorBigKey.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorBigKeyRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorBigKeyResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceMonitorBigKey", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceMonitorBigKeyResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceMonitorBigKeySizeDist(self, request):
        """This API is used to query the big key size distribution of an instance.

        :param request: Request instance for DescribeInstanceMonitorBigKeySizeDist.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorBigKeySizeDistRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorBigKeySizeDistResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceMonitorBigKeySizeDist", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceMonitorBigKeySizeDistResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceMonitorBigKeyTypeDist(self, request):
        """This API is used to query the big key type distribution of an instance

        :param request: Request instance for DescribeInstanceMonitorBigKeyTypeDist.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorBigKeyTypeDistRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorBigKeyTypeDistResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceMonitorBigKeyTypeDist", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceMonitorBigKeyTypeDistResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceMonitorHotKey(self, request):
        """This API is used to query the hot key of an instance.

        :param request: Request instance for DescribeInstanceMonitorHotKey.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorHotKeyRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorHotKeyResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceMonitorHotKey", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceMonitorHotKeyResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceMonitorSIP(self, request):
        """This API is used to query the access source information of an instance.

        :param request: Request instance for DescribeInstanceMonitorSIP.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorSIPRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorSIPResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceMonitorSIP", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceMonitorSIPResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceMonitorTookDist(self, request):
        """This API is used to query the distribution of instance access duration.

        :param request: Request instance for DescribeInstanceMonitorTookDist.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorTookDistRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorTookDistResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceMonitorTookDist", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceMonitorTookDistResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceMonitorTopNCmd(self, request):
        """This API is used to query an instance access command.

        :param request: Request instance for DescribeInstanceMonitorTopNCmd.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorTopNCmdRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorTopNCmdResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceMonitorTopNCmd", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceMonitorTopNCmdResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceMonitorTopNCmdTook(self, request):
        """This API is used to query the instance CPU time.

        :param request: Request instance for DescribeInstanceMonitorTopNCmdTook.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorTopNCmdTookRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceMonitorTopNCmdTookResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceMonitorTopNCmdTook", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceMonitorTopNCmdTookResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeInstanceNodeInfo(self, request):
        """This API is used to query instance node information.

        :param request: Request instance for DescribeInstanceNodeInfo.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceNodeInfoRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeInstanceNodeInfoResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeInstanceNodeInfo", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeInstanceNodeInfoResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeMaintenanceWindow(self, request):
        """This API is used to query instance maintenance window. The maintenance window specifies a time period during which compatible version upgrade, architecture upgrade, backend maintenance, and other operations can be performed to avoid affecting business.

        :param request: Request instance for DescribeMaintenanceWindow.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeMaintenanceWindowRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeMaintenanceWindowResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeMaintenanceWindow", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeMaintenanceWindowResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeProductInfo(self, request):
        """This API is used to query the purchasable capacity specifications of Redis instances in the specified AZ and instance type. If you are not in the allowlist for the AZ or instance type, you cannot view the details of the capacity specifications. To apply for the eligibility, please submit a ticket.

        :param request: Request instance for DescribeProductInfo.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeProductInfoRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeProductInfoResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeProductInfo", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeProductInfoResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeReplicationGroup(self, request):
        """This API is used to query the global replication group.

        :param request: Request instance for DescribeReplicationGroup.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeReplicationGroupRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeReplicationGroupResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeReplicationGroup", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeReplicationGroupResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def DescribeSlowLog(self, request):
        """This API is used to query the slow log.

        :param request: Request instance for DescribeSlowLog.
        :type request: :class:`tencentcloud.redis.v20180412.models.DescribeSlowLogRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.DescribeSlowLogResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeSlowLog", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.DescribeSlowLogResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def InquiryPriceCreateInstance(self, request):
        """This API is used to query the price for purchasing an instance.

        :param request: Request instance for InquiryPriceCreateInstance.
        :type request: :class:`tencentcloud.redis.v20180412.models.InquiryPriceCreateInstanceRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.InquiryPriceCreateInstanceResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("InquiryPriceCreateInstance", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.InquiryPriceCreateInstanceResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def InquiryPriceUpgradeInstance(self, request):
        """This API is used to query the price for scaling an instance.

        :param request: Request instance for InquiryPriceUpgradeInstance.
        :type request: :class:`tencentcloud.redis.v20180412.models.InquiryPriceUpgradeInstanceRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.InquiryPriceUpgradeInstanceResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("InquiryPriceUpgradeInstance", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.InquiryPriceUpgradeInstanceResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def ModfiyInstancePassword(self, request):
        """This API is used to change the Redis password.

        :param request: Request instance for ModfiyInstancePassword.
        :type request: :class:`tencentcloud.redis.v20180412.models.ModfiyInstancePasswordRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.ModfiyInstancePasswordResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("ModfiyInstancePassword", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.ModfiyInstancePasswordResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def ModifyInstanceReadOnly(self, request):
        """This API is used to set instance input mode.

        :param request: Request instance for ModifyInstanceReadOnly.
        :type request: :class:`tencentcloud.redis.v20180412.models.ModifyInstanceReadOnlyRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.ModifyInstanceReadOnlyResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("ModifyInstanceReadOnly", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.ModifyInstanceReadOnlyResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def ReleaseWanAddress(self, request):
        """This API is used to disable public network access.

        :param request: Request instance for ReleaseWanAddress.
        :type request: :class:`tencentcloud.redis.v20180412.models.ReleaseWanAddressRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.ReleaseWanAddressResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("ReleaseWanAddress", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.ReleaseWanAddressResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def UpgradeProxyVersion(self, request):
        """This API is used to upgrade instance proxy version.

        :param request: Request instance for UpgradeProxyVersion.
        :type request: :class:`tencentcloud.redis.v20180412.models.UpgradeProxyVersionRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.UpgradeProxyVersionResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("UpgradeProxyVersion", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.UpgradeProxyVersionResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)


    def UpgradeSmallVersion(self, request):
        """This API is used to upgrade instance minor version.

        :param request: Request instance for UpgradeSmallVersion.
        :type request: :class:`tencentcloud.redis.v20180412.models.UpgradeSmallVersionRequest`
        :rtype: :class:`tencentcloud.redis.v20180412.models.UpgradeSmallVersionResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("UpgradeSmallVersion", params, headers=headers)
            response = json.loads(body)
            if "Error" not in response["Response"]:
                model = models.UpgradeSmallVersionResponse()
                model._deserialize(response["Response"])
                return model
            else:
                code = response["Response"]["Error"]["Code"]
                message = response["Response"]["Error"]["Message"]
                reqid = response["Response"]["RequestId"]
                raise TencentCloudSDKException(code, message, reqid)
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(e.message, e.message)