# [Budy API](http://budy-api.hive.pt)

[Budy](http://budy.hive.pt) API Python client, to be used for simple synchronous integration.

## Configuration

| Name              | Type  | Default                      | Description                                                                                                              |
| ----------------- | ----- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **BUDY_BASE_URL** | `str` | `http://localhost:8080/api/` | The base URL that is going to be used for API connections.                                                               |
| **BUDY_COUNTRY**  | `str` | `US`                         | The country as an ISO 3166-1 to be used for API interactions.                                                            |
| **BUDY_CURRENCY** | `str` | `USD`                        | The [ISO 4217](https://en.wikipedia.org/wiki/ISO_4217) code that describes the currency to be used for API interactions. |
| **BUDY_USERNAME** | `str` | `None`                       | The username to be used for authentication.                                                                              |
| **BUDY_PASSWORD** | `str` | `None`                       | The password to be user for authentication.                                                                              |

## License

Budy API is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://app.travis-ci.com/hivesolutions/budy_api.svg?branch=master)](https://travis-ci.com/github/hivesolutions/budy_api)
[![Build Status GitHub](https://github.com/hivesolutions/budy_api/workflows/Main%20Workflow/badge.svg)](https://github.com/hivesolutions/budy_api/actions)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/budy_api/badge.svg?branch=master)](https://coveralls.io/r/hivesolutions/budy_api?branch=master)
[![PyPi Status](https://img.shields.io/pypi/v/budy_api.svg)](https://pypi.python.org/pypi/budy_api)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
