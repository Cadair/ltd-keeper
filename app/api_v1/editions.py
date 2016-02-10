"""API v1 routes for Editions."""

from datetime import datetime
from flask import jsonify, request

from . import api
from .. import db
from ..auth import token_auth
from ..models import Product, Edition


@api.route('/products/<int:id>/editions/', methods=['POST'])
@token_auth.login_required
def new_edition(id):
    """Create a new Edition for a Product (token required).

    **Example request**

    .. code-block:: http

       POST /v1/products/1/editions/ HTTP/1.1
       Accept: application/json
       Accept-Encoding: gzip, deflate
       Authorization: Basic ZXlKaGJHY2lPaUpJVXpJMU5pSXNJbWxoZENJNk1UUTFOVEUw...
       Connection: keep-alive
       Content-Length: 150
       Content-Type: application/json
       Host: localhost:5000
       User-Agent: HTTPie/0.9.3

       {
           "build_url": "http://localhost:5000/v1/builds/1",
           "published_url": "docs.product.org",
           "slug": "latest",
           "title": "Latest",
           "tracked_refs": "master"
       }

    **Example response**

    .. code-block:: http

       HTTP/1.0 201 CREATED
       Content-Length: 2
       Content-Type: application/json
       Date: Wed, 10 Feb 2016 22:16:50 GMT
       Location: http://localhost:5000/v1/editions/2
       Server: Werkzeug/0.11.3 Python/3.5.0

       {}

    :reqheader Authorization: Include the token in a username field with a
        blank password; ``<token>:``.

    :param id: ID of the product.

    :<json string slug: URL-safe name for edition.
    :<json string title: Human-readable name for edition.
    :<json string build_url: URL of the build entity this Edition uses.
    :<json string tracked_refs: Git ref that this Edition points to. For multi-
        repository builds, this can be a comma-separated list of refs to use,
        in order of priority.
    :<json string published_url: Full URL where this edition is published.

    :statuscode 201: No errors.
    """
    product = Product.query.get_or_404(id)
    edition = Edition(product=product)
    edition.import_data(request.json)
    db.session.add(edition)
    db.session.commit()
    return jsonify({}), 201, {'Location': edition.get_url()}


@api.route('/editions/<int:id>', methods=['DELETE'])
@token_auth.login_required
def deprecate_edition(id):
    """Deprecate an Edition of a Product (token required).

    When an Edition is deprecated, the current time is added to the
    Edition's ``date_ended`` field. Any Edition record with a non-``null``
    ``date_ended`` field will be garbage-collected by LTD Keeper (the
    deletion does not occur immediately upon API request).

    **Example request**

    .. code-block:: http

       DELETE /v1/editions/1 HTTP/1.1
       Accept: */*
       Accept-Encoding: gzip, deflate
       Authorization: Basic ZXlKaGJHY2lPaUpJVXpJMU5pSXNJbWxoZENJNk1UUTFOVEUw...
       Connection: keep-alive
       Content-Length: 0
       Host: localhost:5000
       User-Agent: HTTPie/0.9.3

    **Example response**

    .. code-block:: http

       HTTP/1.0 202 ACCEPTED
       Content-Length: 2
       Content-Type: application/json
       Date: Wed, 10 Feb 2016 23:13:26 GMT
       Server: Werkzeug/0.11.3 Python/3.5.0

       {}

    :statuscode 202: No errors.
    """
    edition = Edition.query.get_or_404(id)
    edition.end_date = datetime.now()
    db.session.commit()
    return jsonify({}), 202


@api.route('/products/<int:id>/editions/', methods=['GET'])
def get_product_editions(id):
    """List all editions published for a Product.

    **Example request**

    .. code-block:: http

       GET /v1/products/1/editions/ HTTP/1.1
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
       Date: Wed, 10 Feb 2016 22:21:49 GMT
       Server: Werkzeug/0.11.3 Python/3.5.0

       {
           "editions": [
               "http://localhost:5000/v1/editions/1",
               "http://localhost:5000/v1/editions/2"
           ]
       }

    :param id: ID of the Product.
    :>json array editions: List of URLs of Edition entities for this Product.
    :statuscode 200: No errors.
    """
    edition_urls = [edition.get_url() for edition in
                    Edition.query.filter(Edition.product_id == id).all()]
    return jsonify({'editions': edition_urls})


@api.route('/editions/<int:id>', methods=['GET'])
def get_edition(id):
    """Show metadata for an Edition.

    **Example request**

    .. code-block:: http

       GET /v1/editions/1 HTTP/1.1
       Accept: */*
       Accept-Encoding: gzip, deflate
       Connection: keep-alive
       Host: localhost:5000
       User-Agent: HTTPie/0.9.3

    **Example response**

    .. code-block:: http

       HTTP/1.0 200 OK
       Content-Length: 387
       Content-Type: application/json
       Date: Wed, 10 Feb 2016 22:29:49 GMT
       Server: Werkzeug/0.11.3 Python/3.5.0

       {
           "build_url": "http://localhost:5000/v1/builds/1",
           "date_created": "2016-02-10T15:14:17.735864Z",
           "date_ended": null,
           "product_url": "http://localhost:5000/v1/products/1",
           "published_url": "docs.product.org",
           "rebuilt_date": "2016-02-10T15:15:09.338565Z",
           "self_url": "http://localhost:5000/v1/editions/1",
           "slug": "latest",
           "title": "Latest",
           "tracked_refs": "master"
       }

    :param id: ID of the Edition.

    :>json string build_url: URL of the build entity this Edition uses.
    :>json string date_created: UTC date time when the edition was created.
    :>json string date_ended: UTC date time when the edition was deprecated;
        will be ``null`` for editions that are *not deprecated*.
    :>json string date_rebuilt: UTC date time when the edition last re-pointed
        to a different build.
    :>json string product_url: URL of parent product entity.
    :>json string published_url: Full URL where this edition is published.
    :>json string self_url: URL of this Edition entity.
    :>json string slug: URL-safe name for edition.
    :>json string title: Human-readable name for edition.
    :>json string tracked_refs: Git ref that this Edition points to. For multi-
        repository builds, this can be a comma-separated list of refs to use,
        in order of priority.

    :statuscode 200: No errors.
    """
    return jsonify(Edition.query.get_or_404(id).export_data())


@api.route('/editions/<int:id>', methods=['PUT'])
@token_auth.login_required
def edit_edition(id):
    """Edit an Edition (token required).

    **Example request**

    .. code-block:: http

       PUT /v1/editions/1 HTTP/1.1
       Accept: application/json
       Accept-Encoding: gzip, deflate
       Authorization: Basic ZXlKaGJHY2lPaUpJVXpJMU5pSXNJbWxoZENJNk1UUTFOVEUw...
       Connection: keep-alive
       Content-Length: 152
       Content-Type: application/json
       Host: localhost:5000
       User-Agent: HTTPie/0.9.3

       {
           "build_url": "http://localhost:5000/v1/builds/1",
           "published_url": "latest.product.org",
           "slug": "latest",
           "title": "Latest",
           "tracked_refs": "master"
       }

    **Example response**

    .. code-block:: http

       HTTP/1.0 200 OK
       Content-Length: 2
       Content-Type: application/json
       Date: Wed, 10 Feb 2016 22:56:32 GMT
       Server: Werkzeug/0.11.3 Python/3.5.0

       {}

    :param id: ID of the Edition.

    :<json string build_url: URL of the build entity this Edition uses.
    :<json string date_ended: UTC date time when the edition was deprecated;
        will be ``null`` for editions that are *not deprecated*.
    :<json string product_url: URL of parent product entity.
    :<json string published_url: Full URL where this edition is published.
    :<json string slug: URL-safe name for edition.
    :<json string title: Human-readable name for edition.
    :<json string tracked_refs: Git ref that this Edition points to. For multi-
        repository builds, this can be a comma-separated list of refs to use,
        in order of priority.

    :statuscode 200: No errors.
    """
    edition = Edition.query.get_or_404(id)
    edition.import_data(request.json)
    db.session.add(edition)
    db.session.commit()
    return jsonify({})