#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from node.node import Node
from node.unl import Unl


def PropagatingtheTX(tx):
    """
    Sends the given transaction to UNL nodes.
    """

    items = {
        "transactionrequest": 1,
        "sequance_number": tx.sequance_number,
        "signature": tx.signature,
        "fromUser": tx.fromUser,
        "to_user": tx.toUser,
        "data": tx.data,
        "amount": tx.amount,
        "transaction_fee": tx.transaction_fee,
        "transaction_time": tx.transaction_time,
    }
    for each_node in Unl.get_as_node_type(Unl.get_unl_nodes()):
        Node.main_node.send_data_to_node(each_node, items)
