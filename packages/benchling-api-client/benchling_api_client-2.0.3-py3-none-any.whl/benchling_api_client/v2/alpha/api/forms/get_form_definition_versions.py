from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.form_definition_versions_paginated_list import FormDefinitionVersionsPaginatedList
from ...models.get_form_definition_versions_sort import GetFormDefinitionVersionsSort
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    form_definition_id: str,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    modified_at: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetFormDefinitionVersionsSort] = GetFormDefinitionVersionsSort.MODIFIEDATDESC,
) -> Dict[str, Any]:
    url = "{}/form-definitions/{form_definition_id}/versions".format(
        client.base_url, form_definition_id=form_definition_id
    )

    headers: Dict[str, Any] = client.httpx_client.headers
    headers.update(client.get_headers())

    cookies: Dict[str, Any] = client.httpx_client.cookies
    cookies.update(client.get_cookies())

    json_sort: Union[Unset, int] = UNSET
    if not isinstance(sort, Unset):
        json_sort = sort.value

    params: Dict[str, Any] = {}
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at
    if not isinstance(json_sort, Unset) and json_sort is not None:
        params["sort"] = json_sort

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[FormDefinitionVersionsPaginatedList, None]]:
    if response.status_code == 200:
        response_200 = FormDefinitionVersionsPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = None

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[FormDefinitionVersionsPaginatedList, None]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    form_definition_id: str,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    modified_at: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetFormDefinitionVersionsSort] = GetFormDefinitionVersionsSort.MODIFIEDATDESC,
) -> Response[Union[FormDefinitionVersionsPaginatedList, None]]:
    kwargs = _get_kwargs(
        client=client,
        form_definition_id=form_definition_id,
        next_token=next_token,
        page_size=page_size,
        modified_at=modified_at,
        sort=sort,
    )

    response = client.httpx_client.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    form_definition_id: str,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    modified_at: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetFormDefinitionVersionsSort] = GetFormDefinitionVersionsSort.MODIFIEDATDESC,
) -> Optional[Union[FormDefinitionVersionsPaginatedList, None]]:
    """Get all versions of a specific form definitions. Form definitions are versioned. This endpoint allows the retrieval of all versions of a specific definition."""

    return sync_detailed(
        client=client,
        form_definition_id=form_definition_id,
        next_token=next_token,
        page_size=page_size,
        modified_at=modified_at,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    form_definition_id: str,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    modified_at: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetFormDefinitionVersionsSort] = GetFormDefinitionVersionsSort.MODIFIEDATDESC,
) -> Response[Union[FormDefinitionVersionsPaginatedList, None]]:
    kwargs = _get_kwargs(
        client=client,
        form_definition_id=form_definition_id,
        next_token=next_token,
        page_size=page_size,
        modified_at=modified_at,
        sort=sort,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    form_definition_id: str,
    next_token: Union[Unset, str] = UNSET,
    page_size: Union[Unset, int] = 50,
    modified_at: Union[Unset, str] = UNSET,
    sort: Union[Unset, GetFormDefinitionVersionsSort] = GetFormDefinitionVersionsSort.MODIFIEDATDESC,
) -> Optional[Union[FormDefinitionVersionsPaginatedList, None]]:
    """Get all versions of a specific form definitions. Form definitions are versioned. This endpoint allows the retrieval of all versions of a specific definition."""

    return (
        await asyncio_detailed(
            client=client,
            form_definition_id=form_definition_id,
            next_token=next_token,
            page_size=page_size,
            modified_at=modified_at,
            sort=sort,
        )
    ).parsed
