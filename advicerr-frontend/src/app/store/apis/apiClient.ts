import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import type { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import type { SerializedError } from "@reduxjs/toolkit";

const DEFAULT_API_BASE_URL = "/api/";

const normalizeApiBaseUrl = (value?: string) => {
  const trimmedValue = value?.trim();

  if (!trimmedValue) {
    return DEFAULT_API_BASE_URL;
  }

  return trimmedValue.endsWith("/") ? trimmedValue : `${trimmedValue}/`;
};

export const apiBaseUrl = normalizeApiBaseUrl(process.env.NEXT_PUBLIC_URL_TO_API);
export const apiBaseQuery = fetchBaseQuery({ baseUrl: apiBaseUrl });

export const resolveApiUrl = (path: string) => `${apiBaseUrl}${path.replace(/^\/+/, "")}`;

const isFetchBaseQueryError = (error: unknown): error is FetchBaseQueryError =>
  typeof error === "object" && error !== null && "status" in error;

const isSerializedError = (error: unknown): error is SerializedError =>
  typeof error === "object" && error !== null && ("message" in error || "code" in error);

const readErrorMessage = (data: unknown) => {
  if (!data || typeof data !== "object") {
    return null;
  }

  const message = "message" in data && typeof data.message === "string" ? data.message : null;
  const detail = "detail" in data && typeof data.detail === "string" ? data.detail : null;

  return detail ?? message;
};

export const describeApiError = (error: unknown, path: string) => {
  const targetUrl = resolveApiUrl(path);

  if (isFetchBaseQueryError(error)) {
    const apiMessage = readErrorMessage(error.data);

    if (apiMessage) {
      return apiMessage;
    }

    if (error.status === "FETCH_ERROR") {
      return `Could not reach ${targetUrl}. Check NEXT_PUBLIC_URL_TO_API (${apiBaseUrl}).`;
    }

    if (error.status === "PARSING_ERROR") {
      return `Received an unexpected response from ${targetUrl}.`;
    }

    if (error.status === "TIMEOUT_ERROR") {
      return `Request to ${targetUrl} timed out.`;
    }

    if (typeof error.status === "number") {
      return `Request to ${targetUrl} failed with status ${error.status}.`;
    }
  }

  if (isSerializedError(error) && error.message) {
    return error.message;
  }

  return `Request to ${targetUrl} failed.`;
};
