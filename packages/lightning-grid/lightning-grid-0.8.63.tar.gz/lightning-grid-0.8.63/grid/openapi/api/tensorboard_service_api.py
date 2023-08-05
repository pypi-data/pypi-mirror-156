# coding: utf-8

"""
    external/v1/external_session_service.proto

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: version not set
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git

    NOTE
    ----
    standard swagger-codegen-cli for this python client has been modified
    by custom templates. The purpose of these templates is to include
    typing information in the API and Model code. Please refer to the
    main grid repository for more info
"""


from __future__ import absolute_import

import re  # noqa: F401
from typing import TYPE_CHECKING, Any

# python 2 and python 3 compatibility library
import six

from grid.openapi.api_client import ApiClient

if TYPE_CHECKING:
    from datetime import datetime
    from grid.openapi.models import *


class TensorboardServiceApi(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

    def tensorboard_service_create_tensorboard(self, cluster_id: 'str', body: 'Body4', **kwargs) -> 'V1CreateTensorboardResponse':  # noqa: E501
        """tensorboard_service_create_tensorboard  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_create_tensorboard(cluster_id, body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param Body4 body: (required)
        :return: V1CreateTensorboardResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.tensorboard_service_create_tensorboard_with_http_info(cluster_id, body, **kwargs)  # noqa: E501
        else:
            (data) = self.tensorboard_service_create_tensorboard_with_http_info(cluster_id, body, **kwargs)  # noqa: E501
            return data

    def tensorboard_service_create_tensorboard_with_http_info(self, cluster_id: 'str', body: 'Body4', **kwargs) -> 'V1CreateTensorboardResponse':  # noqa: E501
        """tensorboard_service_create_tensorboard  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_create_tensorboard_with_http_info(cluster_id, body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param Body4 body: (required)
        :return: V1CreateTensorboardResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['cluster_id', 'body']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tensorboard_service_create_tensorboard" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'cluster_id' is set
        if self.api_client.client_side_validation and ('cluster_id' not in params or
                                                       params['cluster_id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `cluster_id` when calling `tensorboard_service_create_tensorboard`")  # noqa: E501
        # verify the required parameter 'body' is set
        if self.api_client.client_side_validation and ('body' not in params or
                                                       params['body'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `body` when calling `tensorboard_service_create_tensorboard`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'cluster_id' in params:
            path_params['clusterId'] = params['cluster_id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/v1/core/{clusterId}/tensorboards', 'POST',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V1CreateTensorboardResponse',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def tensorboard_service_delete_tensorboard(self, cluster_id: 'str', id: 'str', **kwargs) -> 'V1DeleteTensorboardResponse':  # noqa: E501
        """tensorboard_service_delete_tensorboard  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_delete_tensorboard(cluster_id, id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param str id: (required)
        :return: V1DeleteTensorboardResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.tensorboard_service_delete_tensorboard_with_http_info(cluster_id, id, **kwargs)  # noqa: E501
        else:
            (data) = self.tensorboard_service_delete_tensorboard_with_http_info(cluster_id, id, **kwargs)  # noqa: E501
            return data

    def tensorboard_service_delete_tensorboard_with_http_info(self, cluster_id: 'str', id: 'str', **kwargs) -> 'V1DeleteTensorboardResponse':  # noqa: E501
        """tensorboard_service_delete_tensorboard  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_delete_tensorboard_with_http_info(cluster_id, id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param str id: (required)
        :return: V1DeleteTensorboardResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['cluster_id', 'id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tensorboard_service_delete_tensorboard" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'cluster_id' is set
        if self.api_client.client_side_validation and ('cluster_id' not in params or
                                                       params['cluster_id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `cluster_id` when calling `tensorboard_service_delete_tensorboard`")  # noqa: E501
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `tensorboard_service_delete_tensorboard`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'cluster_id' in params:
            path_params['clusterId'] = params['cluster_id']  # noqa: E501
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/v1/core/{clusterId}/tensorboards/{id}', 'DELETE',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V1DeleteTensorboardResponse',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def tensorboard_service_get_tensorboard(self, cluster_id: 'str', id: 'str', **kwargs) -> 'V1GetTensorboardResponse':  # noqa: E501
        """tensorboard_service_get_tensorboard  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_get_tensorboard(cluster_id, id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param str id: (required)
        :return: V1GetTensorboardResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.tensorboard_service_get_tensorboard_with_http_info(cluster_id, id, **kwargs)  # noqa: E501
        else:
            (data) = self.tensorboard_service_get_tensorboard_with_http_info(cluster_id, id, **kwargs)  # noqa: E501
            return data

    def tensorboard_service_get_tensorboard_with_http_info(self, cluster_id: 'str', id: 'str', **kwargs) -> 'V1GetTensorboardResponse':  # noqa: E501
        """tensorboard_service_get_tensorboard  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_get_tensorboard_with_http_info(cluster_id, id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param str id: (required)
        :return: V1GetTensorboardResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['cluster_id', 'id']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tensorboard_service_get_tensorboard" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'cluster_id' is set
        if self.api_client.client_side_validation and ('cluster_id' not in params or
                                                       params['cluster_id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `cluster_id` when calling `tensorboard_service_get_tensorboard`")  # noqa: E501
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `tensorboard_service_get_tensorboard`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'cluster_id' in params:
            path_params['clusterId'] = params['cluster_id']  # noqa: E501
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/v1/core/{clusterId}/tensorboards/{id}', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V1GetTensorboardResponse',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def tensorboard_service_list_tensorboards(self, cluster_id: 'str', **kwargs) -> 'V1ListTensorboardsResponse':  # noqa: E501
        """tensorboard_service_list_tensorboards  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_list_tensorboards(cluster_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param str page_token:
        :param str limit:
        :param list[str] user_ids:
        :param datetime created_before:
        :param list[str] phase_in:
        :param list[str] phase_not_in:
        :return: V1ListTensorboardsResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.tensorboard_service_list_tensorboards_with_http_info(cluster_id, **kwargs)  # noqa: E501
        else:
            (data) = self.tensorboard_service_list_tensorboards_with_http_info(cluster_id, **kwargs)  # noqa: E501
            return data

    def tensorboard_service_list_tensorboards_with_http_info(self, cluster_id: 'str', **kwargs) -> 'V1ListTensorboardsResponse':  # noqa: E501
        """tensorboard_service_list_tensorboards  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_list_tensorboards_with_http_info(cluster_id, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param str page_token:
        :param str limit:
        :param list[str] user_ids:
        :param datetime created_before:
        :param list[str] phase_in:
        :param list[str] phase_not_in:
        :return: V1ListTensorboardsResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['cluster_id', 'page_token', 'limit', 'user_ids', 'created_before', 'phase_in', 'phase_not_in']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tensorboard_service_list_tensorboards" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'cluster_id' is set
        if self.api_client.client_side_validation and ('cluster_id' not in params or
                                                       params['cluster_id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `cluster_id` when calling `tensorboard_service_list_tensorboards`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'cluster_id' in params:
            path_params['clusterId'] = params['cluster_id']  # noqa: E501

        query_params = []
        if 'page_token' in params:
            query_params.append(('pageToken', params['page_token']))  # noqa: E501
        if 'limit' in params:
            query_params.append(('limit', params['limit']))  # noqa: E501
        if 'user_ids' in params:
            query_params.append(('userIds', params['user_ids']))  # noqa: E501
            collection_formats['userIds'] = 'multi'  # noqa: E501
        if 'created_before' in params:
            query_params.append(('createdBefore', params['created_before']))  # noqa: E501
        if 'phase_in' in params:
            query_params.append(('phaseIn', params['phase_in']))  # noqa: E501
            collection_formats['phaseIn'] = 'multi'  # noqa: E501
        if 'phase_not_in' in params:
            query_params.append(('phaseNotIn', params['phase_not_in']))  # noqa: E501
            collection_formats['phaseNotIn'] = 'multi'  # noqa: E501

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/v1/core/{clusterId}/tensorboards', 'GET',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V1ListTensorboardsResponse',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    def tensorboard_service_update_tensorboard(self, cluster_id: 'str', id: 'str', body: 'Body5', **kwargs) -> 'V1UpdateTensorboardResponse':  # noqa: E501
        """tensorboard_service_update_tensorboard  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_update_tensorboard(cluster_id, id, body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param str id: (required)
        :param Body5 body: (required)
        :return: V1UpdateTensorboardResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('async_req'):
            return self.tensorboard_service_update_tensorboard_with_http_info(cluster_id, id, body, **kwargs)  # noqa: E501
        else:
            (data) = self.tensorboard_service_update_tensorboard_with_http_info(cluster_id, id, body, **kwargs)  # noqa: E501
            return data

    def tensorboard_service_update_tensorboard_with_http_info(self, cluster_id: 'str', id: 'str', body: 'Body5', **kwargs) -> 'V1UpdateTensorboardResponse':  # noqa: E501
        """tensorboard_service_update_tensorboard  # noqa: E501

        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True
        >>> thread = api.tensorboard_service_update_tensorboard_with_http_info(cluster_id, id, body, async_req=True)
        >>> result = thread.get()

        :param async_req bool
        :param str cluster_id: (required)
        :param str id: (required)
        :param Body5 body: (required)
        :return: V1UpdateTensorboardResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['cluster_id', 'id', 'body']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method tensorboard_service_update_tensorboard" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'cluster_id' is set
        if self.api_client.client_side_validation and ('cluster_id' not in params or
                                                       params['cluster_id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `cluster_id` when calling `tensorboard_service_update_tensorboard`")  # noqa: E501
        # verify the required parameter 'id' is set
        if self.api_client.client_side_validation and ('id' not in params or
                                                       params['id'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `id` when calling `tensorboard_service_update_tensorboard`")  # noqa: E501
        # verify the required parameter 'body' is set
        if self.api_client.client_side_validation and ('body' not in params or
                                                       params['body'] is None):  # noqa: E501
            raise ValueError("Missing the required parameter `body` when calling `tensorboard_service_update_tensorboard`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'cluster_id' in params:
            path_params['clusterId'] = params['cluster_id']  # noqa: E501
        if 'id' in params:
            path_params['id'] = params['id']  # noqa: E501

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        # Authentication setting
        auth_settings = []  # noqa: E501

        return self.api_client.call_api(
            '/v1/core/{clusterId}/tensorboards/{id}', 'PUT',
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='V1UpdateTensorboardResponse',  # noqa: E501
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', True),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)
