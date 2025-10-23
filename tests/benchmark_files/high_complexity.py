"""
Benchmark Test File: High Cyclomatic Complexity
Expected Issue: Medium complexity issue on line 1
"""
def process_order(order, user, payment, shipping, inventory, notifications):
    """
    Process an order with multiple validation steps
    WARNING: This function has high cyclomatic complexity (15)
    """
    if order.status == "pending":
        if user.is_verified:
            if payment.is_valid:
                if shipping.address_valid:
                    if inventory.check_stock(order.items):
                        if payment.charge(order.total):
                            for item in order.items:
                                inventory.reduce_stock(item)
                                if item.needs_notification:
                                    notifications.send(user.email, item.name)
                            shipping.create_label(order)
                            order.status = "processing"
                            return True
                        else:
                            payment.refund(order.total)
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    return False
