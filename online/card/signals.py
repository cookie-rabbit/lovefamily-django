from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received


def abc(sender, **kwargs):
    print("success")

def bbc(sender, **kwargs):
    print("failed")


valid_ipn_received.connect(abc)
invalid_ipn_received(bbc)
