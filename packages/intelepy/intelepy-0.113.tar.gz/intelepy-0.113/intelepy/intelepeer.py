import json
import requests


class IntelepeerAPI:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.urlprefix = "https://customer.intelepeer.com"

        data = {"username": self.username, "password": self.password}
        authenticationURL = "https://customer.intelepeer.com/_rest/v4/authenticate"
        headers = {'Content-Type': "application/json", 'Accept': "application/json"}

        ###############################################################################
        ### execute the task and parse results                                      ###
        ###############################################################################
        response = requests.post(authenticationURL, json=data, headers=headers)
        status_code = response.status_code
        text = response.text
        self.token = None
        try:
            self.token = response.json().get(u'token')
        except Exception as E:
            print(E)
        print(u'{}: {}'.format('OK' if response else 'ERROR', response.text))

    def createAccount(self):
        """
        DO NOT USE
        :return:
        """
        url = f"{self.urlprefix}/_rest/v4/my/accounts"
        headers = {'Content-Type': "application/json", 'Authorization': self.token, 'Accept': "application/json"}

    def getAllAccounts(self):
        url = f"{self.urlprefix}/_rest/v4/my/accounts"
        headers = {'Authorization': self.token, 'Accept': "application/json"}
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        text = response.text
        text = json.loads(text)['accounts']
        for x in text:
            print(x)

    def getAccount(self, accountID=None, countNumbers=None, isDeleted=None, name=None, page=None, pageSize=None):
        """
        :param accountID: Account ID(s) to list.
        :param countNumbers: Use this parameter to enrich the results with didCount and tfCount values. Allowed values: 0, 1
        :param isDeleted: Account status; is it deleted. Allowed values: 0, 1
        :param name: Account name, exact match.
        :param page: Which page of results to retrieve.
        :param pageSize: The quantity of accounts to return per page. Between 1 and 100. Must be scalar.
        :return:
        """
        url = f"{self.urlprefix}/_rest/v4/my/accounts"
        extendedurl = f"{self.urlprefix}/_rest/v4/my/accounts?"
        headers = {'Authorization': self.token, 'Accept': "application/json"}
        parameters = {
            "accountID": accountID,
            "countNumbers": countNumbers,
            "isDeleted": isDeleted,
            "name": name,
            "page": page,
            "pageSize": pageSize
        }
        for parameter in parameters:
            if parameters.get(parameter) is not None:
                extendedurl += f'{parameter}={parameters.get(parameter)}&'
                url = extendedurl[:-1]

        response = requests.get(url, headers=headers)
        status_code = response.status_code
        text = response.text

        text = json.loads(text)['accounts']
        if len(text) == 0:
            return None
        return text

    def getAvailableNumberCounts(self, city=None, groupBy=None, npa=None, nxx=None, stateProvince=None,
                                 zeros=None):  # TODO: Finish later
        """
        DO NOT USE
        :param city:
        :param groupBy:
        :param npa:
        :param nxx:
        :param stateProvince:
        :param zeros:
        :return:
        """
        url = f"{self.urlprefix}/_rest/v4/carrier/did/count"
        extendedurl = f"{self.urlprefix}/_rest/v4/carrier/did/count?"
        headers = {'Authorization': self.token, 'Accept': "application/json"}
        parameters = {
            "accountID": accountID,
            "countNumbers": countNumbers,
            "isDeleted": isDeleted,
            "name": name,
            "page": page,
            "pageSize": pageSize
        }
        for parameter in parameters:
            if parameters.get(parameter) is not None:
                extendedurl += f'{parameter}={parameters.get(parameter)}&'
                url = extendedurl[:-1]

    def moveNumbers(self, packageID, endpointsList, email=None, notes=None, referenceID=None):
        """
        :param packageID: The target packageID to order numbers for.
        :param endpointsList: An array of reserved numbers to order Each item is of the e164 form:"+17207998099"
        :param email: An e-mail address to notify about changes in this order's status.
        :param notes: Notes regarding the fulfilment of this order.
        :param referenceID: A non-empty string indicating your reference ID or code.
        :type packageID: Integer
        :type endpointsList: Array
        :return:
        """

        url = f"{self.urlprefix}/_rest/v4/my/did/package"
        headers = {'Content-Type': "application/json", 'Authorization': self.token, 'Accept': "application/json"}
        data = {
            "packageID": packageID,
            "email": email,
            "endpoints": endpointsList,
            "notes": notes,
            "referenceID": referenceID
        }

        for key, value in locals().items():  # loop through arguments given and if any are still set to None, remove from dictionary.
            if value is None:
                data.pop(key)
        response = requests.post(url, json=data, headers=headers)
        text = response.text
        return text

    def getAllPackages(self):
        url = f"{self.urlprefix}/_rest/v4/my/packages"
        extendedurl = f"{self.urlprefix}/_rest/v4/my/packages?"
        headers = {'Authorization': self.token, 'Accept': "application/json"}
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        text = response.text
        text = json.loads(text)['packages']
        if len(text) == 0:
            return None
        return text

