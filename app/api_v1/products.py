"""API v1 routes for products."""

from flask import jsonify, request
from . import api
from .. import db
from ..auth import token_auth
from ..models import Product


@api.route('/products/', methods=['GET'])
def get_products():
    """List all documentation products (anonymous access allowed).

    **Example request**

    .. code-block:: http

       GET /v1/products/ HTTP/1.1
       Accept: */*
       Accept-Encoding: gzip, deflate
       Connection: keep-alive
       Host: localhost:5000
       User-Agent: HTTPie/0.9.3

    **Example response**

    .. code-block:: http

       HTTP/1.0 200 OK
       Content-Length: 108
       Content-Type: application/json
       Date: Tue, 09 Feb 2016 23:48:29 GMT
       Server: Werkzeug/0.11.3 Python/3.5.0

       {
           "products": [
               "http://localhost:5000/v1/products/1",
               "http://localhost:5000/v1/products/2"
           ]
       }

    :>json array products: List of product URLs.
    """
    return jsonify({'products': [product.get_url() for product in
                                 Product.query.all()]})


@api.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    """Get the record of a single documentation product (anonymous access
    allowed).

    **Example request**

    .. code-block:: http

       GET /v1/products/1 HTTP/1.1
       Accept: */*
       Accept-Encoding: gzip, deflate
       Connection: keep-alive
       Host: localhost:5000
       User-Agent: HTTPie/0.9.3

    **Example response**

    .. code-block:: http

       HTTP/1.0 200 OK
       Content-Length: 241
       Content-Type: application/json
       Date: Tue, 09 Feb 2016 23:54:46 GMT
       Server: Werkzeug/0.11.3 Python/3.5.0

       {
           "bucket_name": "an-s3-bucket",
           "doc_repo": "https://github.com/lsst/pipelines_docs.git",
           "domain": "pipelines.lsst.io",
           "self_url": "http://localhost:5000/v1/products/1",
           "slug": "pipelines",
           "title": "LSST Science Pipelines"
       }

    :>json string bucket_name: Name of the S3 bucket hosting builds.
    :>json string doc_repo: URL of the Git documentation repo (i.e., on
       GitHub).
    :>json string domain: Root domain name (without protocol or path) where
       the documentation for this product is served from.
    :>json string title: Human-readable product title.
    :>json string self_url: URL of this Product.
    :>json string slug: URL/path-safe identifier for this product.

    :statuscode 404: Product not found.
    """
    return jsonify(Product.query.get_or_404(id).export_data())


@api.route('/products/', methods=['POST'])
@token_auth.login_required
def new_product():
    """Create a new documentation product (token required).

    **Example request**

    .. code-block:: http

       POST /v1/products/ HTTP/1.1
       Accept: application/json
       Accept-Encoding: gzip, deflate
       Authorization: Basic ZXlKbGVIQWlPakUwTlRVd05qUXdNVElzSW1Gc1p5STZJa2hU...
       Connection: keep-alive
       Content-Length: 176
       Content-Type: application/json
       Host: localhost:5000
       User-Agent: HTTPie/0.9.3

       {
           "bucket_name": "an-s3-bucket",
           "doc_repo": "https://github.com/lsst/pipelines_docs.git",
           "domain": "pipelines.lsst.io",
           "slug": "pipelines",
           "title": "LSST Science Pipelines"
       }

    **Example response**

    .. code-block:: http

       HTTP/1.0 201 CREATED
       Content-Length: 2
       Content-Type: application/json
       Date: Tue, 09 Feb 2016 23:35:18 GMT
       Location: http://localhost:5000/v1/products/1
       Server: Werkzeug/0.11.3 Python/3.5.0

       {}

    :reqheader Authorization: Include the token in a username field with a
        blank password; ``<token>:``.
    :<json string slug: URL/path-safe identifier for this product.
    :<json string doc_repo: URL of the Git documentation repo (i.e., on
       GitHub).
    :<json string title: Human-readable product title.
    :<json string domain: Root domain name (without protocol or path) where
       the documentation for this product is served from.
    :<json string bucket_name: Name of the S3 bucket hosting builds.
    :resheader Location: URL of the created product.
    :statuscode 201: no error
    """
    product = Product()
    product.import_data(request.json)
    db.session.add(product)
    db.session.commit()
    return jsonify({}), 201, {'Location': product.get_url()}


@api.route('/products/<int:id>', methods=['PUT'])
@token_auth.login_required
def edit_product(id):
    """Update a product (token required).

    See :http:post:`/v1/products/` for documentation on the JSON-formatted
    message body.

    :reqheader Authorization: Include the token in a username field with a
        blank password; ``<token>:``.
    :statuscode 404: Product not found.
    """
    product = Product.query.get_or_404(id)
    product.import_data(request.json)
    db.session.add(product)
    db.session.commit()
    return jsonify({})