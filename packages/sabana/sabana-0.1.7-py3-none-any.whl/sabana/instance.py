from google.protobuf.json_format import ParseDict
from os import getenv
import sys

from sabana.common import (
    ndarray_from_values,
    post,
    get_config,
    get_access_token,
    get_id_token,
    TokenError,
    PostError,
    login_msg,
)
from sabana.responses import is_error, is_read, execute_response


class InstanceError(Exception):
    pass


class Instance:
    """
    Instance: handler for an instance in the Sabana platform.

              Can be created either by specifying user, instance, tag
              or by providing a URL.
    """

    __endpoint = "https://deploy.sabana.io"

    def __init__(self, instance=None):
        try:
            config = get_config()
            self.access_token = get_access_token(config)
            self.id_token = get_id_token(config)
        except TokenError:
            self.access_token = getenv("SABANA_ACCESS_TOKEN")
            self.id_token = getenv("SABANA_ID_TOKEN")
            if not isinstance(self.access_token, str) or not isinstance(
                self.id_token, str
            ):
                print("ERROR: Could not find credentials on local file or environment.")
                print(
                    "       Use the following command to log-in using the Sabana CLI:\n"
                )
                print("sabana login\n")
                print("Alternatively setup the following environment variables:")
                print("SABANA_ACCESS_TOKEN, SABANA_ID_TOKEN")
                sys.exit(-1)
        except Exception as e:
            print("Fatal error trying to get credentials by the Instance object.")
            print("Contact Sabana for support.")
            sys.exit(-1)

        self.instance_url = None
        self.user = None
        self.instance = None
        self.tag = None
        self.is_up = False

        if instance[:8] == "https://":
            self.instance_url = instance
        elif (":" in instance) and (len(instance.split("/")) == 2):
            (prefix, self.tag) = instance.split(":")
            (self.user, self.instance) = prefix.split("/")
        else:
            raise InstanceError("Define user, instance, and tag, or a url")

    def __str__(self) -> str:
        msg = "Sabana Instance:\n"
        if all(isinstance(i, str) for i in (self.user, self.instance, self.tag)):
            msg += f"Instance: {self.user}/{self.instance}:{self.tag}\n"
        if isinstance(self.instance_url, str):
            msg += f"Deployed at: {self.instance_url}"
        return msg

    def __del__(self):
        try:
            isup = self.is_up
        except AttributeError:
            # If the user tries to create an object with wrong arguments
            # this function will be called without self.is_up being defined.
            pass
        else:
            if self.is_up:
                self.down()

    def up(self):
        url = "{}/api/v0/up".format(self.__endpoint)
        req = {
            "user": self.user,
            "instance": self.instance,
            "tag": self.tag,
        }

        try:
            res = post(req, url, self.access_token, self.id_token)
        except TokenError as e:
            print(login_msg)
            raise InstanceError(login_msg)
        except PostError as e:
            raise InstanceError("Failed bringing instance up: {}".format(e))
        else:
            if not "url" in res:
                print(login_msg)
                raise InstanceError("not able to up that instance")
            if len(res["url"]) == 0:
                raise InstanceError("Got invalid URL from server.")
            else:
                self.instance_url = res["url"]
                self.is_up = True
                print(
                    "Instance {}/{}:{} is up".format(self.user, self.instance, self.tag)
                )
                print(self.instance_url)

    def down(self):
        url = "{}/api/v0/down".format(self.__endpoint)
        req = {
            "url": self.instance_url,
        }
        try:
            res = post(req, url, self.access_token, self.id_token)
        except Exception as e:
            raise InstanceError(
                "Failed bringing {}/{}:{} down: {}".format(
                    self.user, self.instance, self.tag, str(e)
                )
            )
        else:
            print(
                "Instance {}/{}:{} is down".format(self.user, self.instance, self.tag)
            )
            self.is_up = False
            self.instance_url == ""

    def execute(self, program):
        if not self.is_up and self.instance_url == "":
            raise InstanceError("Need to deploy an instance to execute this program")

        url = "{}/api/v0/execute".format(self.__endpoint)
        req = {
            "url": self.instance_url,
            "program": program.to_dict(),
        }

        try:
            response = post(req, url, self.access_token, self.id_token)
        except TokenError as e:
            print(login_msg)
            raise InstanceError(login_msg)
        except PostError as e:
            raise InstanceError("Failed executing the program: {}".format(e))
        else:
            reference = execute_response()
            res = ParseDict(response, reference)

            if len(program.req.requests) > 0 and len(res.responses) == 0:
                raise InstanceError("Execute failed with no responses")
            else:
                values = []
                for (a, b, i) in zip(
                    program.req.requests,
                    res.responses,
                    range(len(program.req.requests)),
                ):
                    if is_error(b.outcome):
                        msg = "\nOperation number {}: \n{} - {}\nfailed with: {}\n".format(
                            i, a.resource, str(a), b.outcome.info
                        )
                        raise InstanceError(msg)
                    elif is_read(b):
                        values.append(
                            ndarray_from_values(b.read.values, b.read.datatype).reshape(
                                b.read.shape
                            )
                        )
                return values
