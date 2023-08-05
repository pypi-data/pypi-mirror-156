:title: Configuration

Configuration
=============

The web client will look by default for a ``$HOME/.config/zuul/client.conf`` or a ``$HOME/.zuul.conf``
file for its configuration. The file should consist of a ``[webclient]`` section with at least
the ``url`` attribute set. The optional ``verify_ssl`` can be set to False to
disable SSL verifications when connecting to Zuul (defaults to True). An
authentication token can also be stored in the configuration file under the attribute
``auth_token`` to avoid passing the token in the clear on the command line.
A default tenant can also be set with the ``tenant`` attribute.

Here is an example of a configuration file that can be used with zuul-client:

.. literalinclude:: /examples/.zuul.conf
   :language: ini


It is also possible to run the web client without a configuration file, by using the
``--zuul-url`` option to specify the base URL of the Zuul web server.
