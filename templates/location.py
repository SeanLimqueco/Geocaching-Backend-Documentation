from flask import abort, make_response
from geocache.models import CacheLocation, cache_location_schema, cache_locations_schema, db


def create(body):  # this was the error here
    '''
    Handles the creation of new Cache locations.
    Checks to see if a Cache Location name has been taken. if not then it will create a
    new cache location based off the given information, otherwise it will throw an error.

    @param body - A JSON file containing the newly made cache.
    @return return cache_location_schema.dump(new_cache_location), 201 - a tuple that converts 
        new_cache_location to a JSON file and returns HTTP code 201 (SUCCESSFUL POST)
    '''
    existing_cache_location = CacheLocation.query.filter(
        CacheLocation.cachename == body.get('cachename')).one_or_none()

    if existing_cache_location is None:
        # loads the JSON file (body) into python using the SQLAlchemy session attatched to the db
        new_cache_location = cache_location_schema.load(body, session=db.session)

        # Add the new_cache_location to the db
        db.session.add(new_cache_location)
        db.session.commit()

        # returns the new_cache_location in the form of a JSON file, confirming this with the
        # HTTP status code 201 (SUCCESSFUL POST)
        return cache_location_schema.dump(new_cache_location), 201
    else:
        # Throws an error using HTTP status code 406 (NOT ACCEPTABLE)
        abort(406, f"Cache location with name {body.get('cachename')} already exists")


def read_all():
    '''
    Pulls up all the Cache Locations, dumps them into JSON files, then returns them.
    '''
    cache_locations = CacheLocation.query.all()
    return cache_locations_schema.dump(cache_locations)


def read_one(location_id: int):
    '''
    Checks for a Cache Location based on its ID and returns it if it exists.

    @param location_id: int - location ID for the Cache Location
    @return cache_location_schema.dump(cache_location) - a JSON file of the requested cache_location
    '''
    cache_location = CacheLocation.query.filter(CacheLocation.id == location_id).one_or_none()

    if cache_location is not None:
        return cache_location_schema.dump(cache_location)
    else:
        abort(404, f"Cache location with id {location_id} not found")


def update(location_id: int, body):
    existing_cache_location = CacheLocation.query.filter(CacheLocation.id == location_id).one_or_none()
    if existing_cache_location:
        existing_cache_location = cache_location_schema.load(body, instance=existing_cache_location)
        db.session.merge(existing_cache_location)
        db.session.commit()
        return cache_location_schema.dump(existing_cache_location), 201
    else:
        abort(404, f"Cache location with id {location_id} not found")


def delete(location_id: int):
    existing_cache_location = CacheLocation.query.filter(CacheLocation.id == location_id).one_or_none()

    if existing_cache_location:
        db.session.delete(existing_cache_location)
        db.session.commit()
        # @FIXME this message is not coming across and unconvincing reply in API Return
        return cache_location_schema.dump(existing_cache_location), 204
    else:
        abort(404, f"Location with id {location_id} not found")


def verify_code(verification_string: str):
    cache_location = CacheLocation.query.filter(
        CacheLocation.verificationString == verification_string).first()

    if cache_location is not None:
        return cache_location_schema.dump(cache_location)
    else:
        abort(404, f"No cache found with matching verification string: {verification_string} not found")
