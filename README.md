# ** This repository is no longer maintained! ** 
Our current Python SDK can be found <a href="https://github.com/globalpayments/python-sdk" target="_blank">here</a>

<a href="http://developer.heartlandpaymentsystems.com/SecureSubmit" target="_blank">
	<img src="http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-heartland-logo" alt="Heartland logo" title="Heartland" align="right" />
</a>

# Heartland Python SDK

This SDK makes it easy to integrate your Python application with Heartland's [**Portico Gateway API**](http://developer.heartlandpaymentsystems.com/Portico). Supported features include:

* Card Not Present (eCommerce and mobile)
* Card Present (Retail and Restaurant)
* <a href="http://developer.heartlandpaymentsystems.com/SecureSubmit" target="_blank">Secure Submit</a> single-use tokenization and multi-use tokenization
* <a href="https://www.heartlandpaymentsystems.com/about-heartland-secure/" target="_blank">Heartland Secure</a> End-to-End Encryption (E3)
* [Credit](http://developer.heartlandpaymentsystems.com/Documentation/credit-card-payments/), [Gift & Loyalty](http://developer.heartlandpaymentsystems.com/Documentation/gift-card-payments/)</a>,and eCheck/ACH
* [Recurring Payments](http://developer.heartlandpaymentsystems.com/Documentation/recurring-payments/)


|  <a href="#data-security"><b>Data Security</b></a> | <a href="#documentation-and-examples"><b>API Reference</b></a>  |  <a href="#testing--certification"><b>Testing & <br>Certification</b></a> | <a href="#api-keys"><b>API Keys</b></a> | Links |
|:--:|:--:|:--:|:--:|:--|
| [![](http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-icon-secure)](#data-security)  | [![](http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-icon-resources)](#documentation-and-examples)  | [![](http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-icon-tools)](#testing--certification) | [![](http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-icon-keys)](#api-keys) | <a href="http://developer.heartlandpaymentsystems.com/Account/Register" target="_blank">Register an Account</a> <br> <a href="http://developer.heartlandpaymentsystems.com/Partnership" target="_blank">Partner with Heartland</a> <br>  |


####Developer Support

You are not alone! If you have any questions while you are working through your development process, please feel free to <a href="https://developer.heartlandpaymentsystems.com/Support" target="_blank">reach out to our team for assistance</a>!


## Requirements
 1. Python 2.7.9  (Python 3 is not yet supported)


## Installation

You can use [Pip](https://en.wikipedia.org/wiki/Pip_(package_manager)) to install the SDK. Most distributions of Python come with pip pre-installed. To install enter the following :

> $ python pip install SecureSubmit


## API Keys

<img src="http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-icon-keys" align="right"/>
Integrations that use card not present transactions, such as eCommerce web applications, will use API keys to authenticate. There are exceptions, such as card present POS integrations. For these projects please <a href="https://developer.heartlandpaymentsystems.com/Support" target="_blank">contact us</a> for more information.  

To begin creating test transactions you will need to obtain a set of public and private keys. These are easily obtained by creating an account on our [developer portal](http://developer.heartlandpaymentsystems.com/).
Your keys are located under your profile information. 

[![Developer Keys](http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-devportal-keys)](http://developer.heartlandpaymentsystems.com/Account/KeysAndCredentials)

You will use your public key when implementing card tokenization and your private key will be used when communicating with our Portico Gateway. More details can be found in our [documentation](http://developer.heartlandpaymentsystems.com/SecureSubmit).

Note: Multi-Use tokenization is not enabled by default when creating an account. You can contact <a href="mailto:SecureSubmitCert@e-hps.com?subject=Multi-use Token Request&body=Please enable multi-use tokens on my developer portal account which was signed up under the following email : ">Heartland's Specialty Products Team</a> to have this enabled. This is also true if you wish to use Gift & Loyalty, ACH, and Debit.


## Data Security
 
 <img src="http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-icon-secure" align="right"/>
 If your app stores, processes, or transmits cardholder data in cleartext then it is in-scope for <a href="https://www.pcisecuritystandards.org/document_library?category=padss" target="_blank">PA-DSS</a>. If your app is hosted, or the data in question otherwise comes into your organization, then the app and your entire company are in-scope for <a href="https://www.pcisecuritystandards.org/document_library?document=pci_dss" target="_blank">PCI DSS</a> (either as a merchant or a service provider). Heartland offers a suite of solutions to help keep integrators' applications and/or environments shielded from cardholder data, whether it motion or at rest.
 
 * **Secure Submit** for eCommerce web or mobile applications ("card-not-present"), which leverages single-use tokenization to prevent card data from passing through the merchant or integrator's webserver. It only requires a simple JavaScript inclusion and provides two options for payment field hosting:
 
  * **Self-Hosted Fields** - this approach relies upon the standard, appropriately named, HTML form controls on the integrator's served web page.
  
  - **Heartland Hosted Fields** - this approach combines the Secure Submit service with iframes to handle presentation of the form fields and collection of sensitive data on Heartland servers. Since PCI version 3.1 the PCI Council and many QSAs advocate the iframe-based approach as enabling a merchant to more readily achieve PCI compliance via the simplified <a href="https://www.pcisecuritystandards.org/documents/PCI-DSS-v3_2-SAQ-A_EP.pdf" target="_blank">SAQ A-EP</a> form. Check out the CoalFire's [whitepaper](http://developer.heartlandpaymentsystems.com/Resource/Download/coalfire-white-paper) for more information.
  
 - **Heartland Secure** for card-present retailers, hospitality, and other "POS" applications, comprises three distinct security technologies working in concert:
  - **End-to-End Encryption** (E3) - combines symmetric and asymmetric cryptography to form an "Identity-Based Encryption" methodology which keeps cardholder data encrypted from the moment of the swipe.
  
  - **Tokenization** - replaces sensitive data values with non-sensitive representations which may be stored for recurring billing, future orders, etc.
  
  - **EMV** - though less about data security and more about fraud prevention, EMV or chip card technology guarantees the authenticity of the payment card and is thus an important concern for retailers.
 
 Depending on your (or your customers') payment acceptance environment, you may need to support one or more of these technologies in addition to this SDK. This SDK also supports the ability to submit cleartext card numbers as input, but any developer who does so will be expected to demonstrate compliance with PA-DSS. Likewise any third party integrator who is planning on handling cleartext card data on behalf of other merchants will be expected to demonstrate their PCI DSS compliance as a Service Provider prior to completing certification with Heartland.
 
 If you implement Secure Submit tokenization for your web or mobile application you will never have to deal with handling a card number - Heartland will take care of it for you and return a token to initiate the charge from your servers.
 
 Similarly, if you implement Heartland Secure with E3 (for both swiped and keyed entry methods) then your POS application will be out-of-scope for PA-DSS. Heartland Secure certified devices will only ever return E3 encrypted data which can safely be passed through your systems as input to this SDK. Heartland Secure devices include many popular models manufactured by PAX and Ingenico.
 
 
To summarize, when you create a `paymentMethod` using this SDK you have the following options for securely avoiding interaction with sensitive cardholder data:
 
* Card data (track or PAN) may be sent directly from a web browser to Heartland, returning a SecureSubmit single use token that is then sent to your server.
 
* Encrypted card data (track or PAN) may be obtained directly from a Heartland Secure device and passed to the SDK


## Documentation and Examples

 <img src="http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-icon-resources" align="right"/>
  You can find the latest SDK documentation along with code examples on our [Developer Portal](http://developer.heartlandpaymentsystems.com/documentation).
  In addition you can find working examples in the our example code repository:

  * [Django End-to-End](http://github.hps.com/DevPortal/Python-SDK/tree/master/examples/django/end_to_end)
  * [Webpy End-to-End](http://github.hps.com/DevPortal/Python-SDK/tree/master/examples/webpy/end_to_end)

*Quick Tip*: The included [test suite](http://github.hps.com/DevPortal/Python-SDK/tree/master/securesubmit/tests) can be a great source of code samples for using the SDK!

#### Fluent Interface

Note that our SDK provides a [Fluent Interface](https://en.wikipedia.org/wiki/Fluent_interface) which allows you to replace a charge call that looks like this:

 ```python
 response = self.(10, "USD", card_data, card_holder, False, None, False, None, None, False, True, True):
 ````

 With one that reads like this:

 ```python
 response = self.service.charge(10)\
    .with_card(TestCreditCard.valid_visa)\
    .with_card_holder(TestCardHolder.valid_card_holder)\
    .with_allow_duplicates(True)\
    .execute()

````

Between the two samples you can more easily read and understand what the code is doing in the second example than the first. That is a big advantage and helps speed development and reduce errors when using methods that allow a large number of parameters.


## Testing & Certification

<img src="http://developer.heartlandpaymentsystems.com/Resource/Download/sdk-readme-icon-tools" align="right"/>
Testing your implementation in our Certification/Sandbox environment helps to identify and squash bugs before you begin processing transactions in the production environment. While you are encouraged to run as many test transactions as you can, Heartland provides a specific series of tests that you are required to complete before receiving Certification. Please contact Heartland to initiate certification for your integration. For eComm integrations please email our <a href="mailto:SecureSubmitCert@e-hps.com?Subject=Certification Request&Body=I am ready to start certifying my integration! ">Specialty Products Team</a>, for POS developers please email <a href="mailto:integration@e-hps.com?Subject=Certification Request&Body=I am ready to start certifying my integration! ">Integrations</a>. 

*Quick Tip*: You can get a head start on your certification by reviewing the [certification tests](http://github.hps.com/DevPortal/Python-SDK/tree/master/securesubmit/tests) in the included test suite.

####Test Card Data

The following card numbers are used by our Certification environment to verify that your tests worked. Note that while variations (such as 4111111111111111) will work for general testing the cards listed below are required to complete certification. 

<table align="center">
	<thead>
		<tr>
			<th scope="col">Name</th>
			<th scope="col">Number</th>
			<th scope="col">Exp Month</th>
			<th scope="col">Exp Year</th>
			<th scope="col">CVV</th>
			<th scope="col">Address</th>
			<th scope="col">Zip</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td>Visa</td>
			<td>4012002000060016</td>
			<td>12</td>
			<td>2025</td>
			<td>123</td>
			<td>6860 Dallas Pkwy</td>
			<td>75024</td>
		</tr>
		<tr>
			<td>MasterCard</td>
			<td>5473500000000014</td>
			<td>12</td>
			<td>2025</td>
			<td>123</td>
			<td>6860 Dallas Pkwy</td>
			<td>75024</td>
		</tr>
		<tr>
			<td>Discover</td>
			<td>6011000990156527</td>
			<td>12</td>
			<td>2025</td>
			<td>123</td>
			<td>6860 Dallas Pkwy</td>
			<td>75024</td>
		</tr>
		<tr>
			<td>Amex</td>
			<td>372700699251018</td>
			<td>12</td>
			<td>2025</td>
			<td>1234</td>
			<td>6860 Dallas Pkwy</td>
			<td>75024</td>
		</tr>
		<tr>
			<td>JCB</td>
			<td>3566007770007321</td>
			<td>12</td>
			<td>2025</td>
			<td>123</td>
			<td>6860 Dallas Pkwy</td>
			<td>75024</td>
		</tr>
	</tbody>
</table>

####Testing Exceptions

During your integration you will want to test for specific issuer responses such as 'Card Declined'. Because our sandbox does not actually reach out to issuers we have devised specific transaction amounts that will trigger  [issuer response codes](https://cert.api2.heartlandportico.com/Gateway/PorticoDevGuide/build/PorticoDeveloperGuide/Issuer%20Response%20Codes.html) and [gateway response codes](https://cert.api2.heartlandportico.com/Gateway/PorticoDevGuide/build/PorticoDeveloperGuide/Gateway%20Response%20Codes.html). Please <a href="mailto:SecureSubmitCert@e-hps.com?subject=Hard Coded Values Spreadsheet Request">contact</a> Heartland for a complete listing of values you can charge to simulate AVS, CVV and Transaction declines, errors, and other responses that you can catch in your code:

```python
try:
    credit_service.charge(-5, 'usd', credit_card, card_holder)
except HpsInvalidRequestException, e:
    # handle error for amount less than zero dollars
except HpsAuthenticationException, e:
    # handle errors related to your HpsServiceConfig
except HpsCreditException, e:
    # handle card-related exceptions: card declined, processing error, etc
````

More exceptions can be found [here](http://github.hps.com/DevPortal/Python-SDK/tree/master/securesubmit/infrastructure/__init__.py) and issuer responses [here](http://github.hps.com/DevPortal/Python-SDK/tree/master/securesubmit/infrastructure/validation.py#L18-L81).

## Contributing

All our code is open sourced and we encourage fellow developers to contribute and help improve it!

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Ensure SDK tests are passing
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin my-new-feature`)
6. Create new Pull Request


####Included Test Suite

The included test suite can help ensure your contribution doesn't cause unexpected errors and is a terrific resource of working examples that you can reference. As mentioned earlier, the [certification folder](http://github.hps.com/DevPortal/Python-SDK/tree/master/securesubmit/tests/certification) contains tests that mirror the types of requirements you will encounter when you certify your integration for production.


