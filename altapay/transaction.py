from __future__ import absolute_import, unicode_literals

import altapay.callback
from altapay import exceptions
from altapay.resource import Resource


class Transaction(Resource):
    @classmethod
    def find(cls, transaction_id, api):
        """
        Find exactly one transaction by a transaction ID.

        :param transaction_id: ID of the transaction in AltaPay
        :param api: An API object which will be used for AltaPay communication.

        :rtype: :py:class:`altapay.Transaction`
        """
        response = api.get(
            'API/payments', parameters={'transaction_id': transaction_id}
        )['APIResponse']

        try:
            transaction = response['Body']['Transactions']['Transaction']
        except KeyError:
            raise exceptions.ResourceNotFoundError(
                'No Transaction found matching transaction ID: {}'.format(
                    transaction_id))

        if isinstance(transaction, list):
            raise exceptions.MultipleResourcesError(
                'More than one Payment was found. Total found is: {}'.format(
                    len(response['Body']['Transactions'])))

        return cls(
            response['@version'], response['Header'], transaction, api=api)

    def capture(self, **kwargs):
        """
        Capture a reservation on a transaction.

        :param \*\*kwargs: used for optional capture parameters, see the
            AltaPay documentation for a full list.
            Note that you will need to use lists and dictionaries to map the
            URL structures from the AltaPay documentation into these kwargs.
        """
        parameters = {
            'transaction_id': self.transaction_id
        }

        parameters.update(kwargs)

        response = self.api.get(
            'API/captureReservation', parameters=parameters)['APIResponse']

        return Transaction(
            response['@version'], response['Header'],
            response['Body']['Transactions']['Transaction'], api=self.api)

    def charge_subscription(self, **kwargs):
        """
        This will charge a subscription using a capture. Can be called many
        times on a subscription.

        If amount is not sent as an optinal parameter, the amount specified in
        the original setup of the subscription will be used.

        :param \*\*kwargs: used for optional charge subscription parameters,
            see the AltaPay documentation for a full list.
            Note that you will need to use lists and dictionaries to map the
            URL structures from the AltaPay documentation into these kwargs.

        :rtype: :py:class:`altapay.Callback` object.
        """
        parameters = {
            'transaction_id': self.transaction_id
        }

        parameters.update(kwargs)

        response = self.api.get(
            'API/chargeSubscription', parameters=parameters)['APIResponse']

        return altapay.callback.Callback.from_xml_callback(response)

    def reserve(self, **kwargs):
        """
        This will create a reservation on a subscription. Can be called many
        times on a subscription.

        If amount is not sent as an optinal parameter, the amount specified in
        the original setup of the subscription will be used.

        :param \*\*kwargs: used for optional reserve subscription parameters,
            see the AltaPay documentation for a full list.
            Note that you will need to use lists and dictionaries to map the
            URL structures from the AltaPay documentation into these kwargs.

        :rtype: :py:class:`altapay.Callback` object.
        """
        parameters = {
            'transaction_id': self.transaction_id
        }

        parameters.update(kwargs)

        response = self.api.get(
            'API/reserveSubscriptionCharge',
            parameters=parameters)['APIResponse']

        return altapay.callback.Callback.from_xml_callback(response)
