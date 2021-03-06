'''A collection of interfaces that CKAN plugins can implement to customize and
extend CKAN.

'''
__all__ = [
    'Interface',
    'IGenshiStreamFilter', 'IRoutes',
    'IMapper', 'ISession',
    'IMiddleware',
    'IAuthFunctions',
    'IDomainObjectModification', 'IGroupController',
    'IOrganizationController',
    'IPackageController', 'IPluginObserver',
    'IConfigurable', 'IConfigurer',
    'IActions', 'IResourceUrlChange', 'IDatasetForm',
    'IValidators',
    'IResourcePreview',
    'IResourceView',
    'IResourceController',
    'IGroupForm',
    'ITagController',
    'ITemplateHelpers',
    'IFacets',
    'IAuthenticator',
]

from inspect import isclass
from pyutilib.component.core import Interface as _pca_Interface


class Interface(_pca_Interface):

    @classmethod
    def provided_by(cls, instance):
        return cls.implemented_by(instance.__class__)

    @classmethod
    def implemented_by(cls, other):
        if not isclass(other):
            raise TypeError("Class expected", other)
        try:
            return cls in other._implements
        except AttributeError:
            return False


class IMiddleware(Interface):
    '''Hook into Pylons middleware stack
    '''
    def make_middleware(self, app, config):
        '''Return an app configured with this middleware
        '''
        return app

    def make_error_log_middleware(self, app, config):
        '''Return an app configured with this error log middleware
        '''
        return app


class IGenshiStreamFilter(Interface):
    '''
    Hook into template rendering.
    See ckan.lib.base.py:render
    '''

    def filter(self, stream):
        """
        Return a filtered Genshi stream.
        Called when any page is rendered.

        :param stream: Genshi stream of the current output document
        :returns: filtered Genshi stream
        """
        return stream


class IRoutes(Interface):
    """
    Plugin into the setup of the routes map creation.

    """
    def before_map(self, map):
        """
        Called before the routes map is generated. ``before_map`` is before any
        other mappings are created so can override all other mappings.

        :param map: Routes map object
        :returns: Modified version of the map object
        """
        return map

    def after_map(self, map):
        """
        Called after routes map is set up. ``after_map`` can be used to
        add fall-back handlers.

        :param map: Routes map object
        :returns: Modified version of the map object
        """
        return map


class IMapper(Interface):
    """
    A subset of the SQLAlchemy mapper extension hooks.
    See http://www.sqlalchemy.org/docs/05/reference/orm/interfaces.html#sqlalchemy.orm.interfaces.MapperExtension

    Example::

        >>> class MyPlugin(SingletonPlugin):
        ...
        ...     implements(IMapper)
        ...
        ...     def after_update(self, mapper, connection, instance):
        ...         log("Updated: %r", instance)
    """

    def before_insert(self, mapper, connection, instance):
        """
        Receive an object instance before that instance is INSERTed into
        its table.
        """

    def before_update(self, mapper, connection, instance):
        """
        Receive an object instance before that instance is UPDATEed.
        """

    def before_delete(self, mapper, connection, instance):
        """
        Receive an object instance before that instance is DELETEed.
        """

    def after_insert(self, mapper, connection, instance):
        """
        Receive an object instance after that instance is INSERTed.
        """

    def after_update(self, mapper, connection, instance):
        """
        Receive an object instance after that instance is UPDATEed.
        """

    def after_delete(self, mapper, connection, instance):
        """
        Receive an object instance after that instance is DELETEed.
        """


class ISession(Interface):
    """
    A subset of the SQLAlchemy session extension hooks.
    """

    def after_begin(self, session, transaction, connection):
        """
        Execute after a transaction is begun on a connection
        """

    def before_flush(self, session, flush_context, instances):
        """
        Execute before flush process has started.
        """

    def after_flush(self, session, flush_context):
        """
        Execute after flush has completed, but before commit has been called.
        """

    def before_commit(self, session):
        """
        Execute right before commit is called.
        """

    def after_commit(self, session):
        """
        Execute after a commit has occured.
        """

    def after_rollback(self, session):
        """
        Execute after a rollback has occured.
        """


class IDomainObjectModification(Interface):
    """
    Receives notification of new, changed and deleted datasets.
    """

    def notify(self, entity, operation):
        pass

    def notify_after_commit(self, entity, operation):
        pass


class IResourceUrlChange(Interface):
    """
    Receives notification of changed urls.
    """

    def notify(self, resource):
        pass


class IResourceView(Interface):
    '''Add custom data view for resource file-types.

    '''
    def info(self):
        '''
        Return configuration for the view. Info can return the following.

        :param name: name of view type
        :param title: title of view type (Optional)
        :param schema: schema to validate extra view config (Optional)
        :param icon: icon from
            http://fortawesome.github.io/Font-Awesome/3.2.1/icons/
            without the icon- prefix eg. compass (Optional).
        :param iframed: should we iframe the view template before rendering.
            If the styles or JavaScript clash with the main site theme this
            should be set to true. Default is true. (Optional)
        :param preview_enabled:
            Says if the preview button appears for this resource. Some preview
            types have their  previews integrated with the form.
            Some preview types have their previews integrated with the form.
            Default false (Optional)
        :param full_page_edit:  Says if the edit form is the full page width
            of the page. Default false (Optional)

        eg:
            {'name': 'image_view',
             'title': 'Image',
             'schema': {'image_url': [ignore_empty, unicode]},
             'icon': 'compass',
             'iframed': false,
             }

        '''
        return {'name': self.__class__.__name__}

    def can_view(self, data_dict):
        '''Return info on whether the plugin can preview the resource.
        The ``data_dict`` contains: ``resource`` and ``package``.

        return ``True`` or ``False``.
        '''

    def setup_template_variables(self, context, data_dict):
        '''
        Add variables to the ``data_dict`` that is passed to the
        template being rendered.
        Should return a new dict instead of updating the input ``data_dict``.

        The ``data_dict`` contains: ``resource_view``, ``resource`` and
        ``package``.
        '''

    def view_template(self, context, data_dict):
        '''
        Returns a string representing the location of the template to be
        rendered when the view is rendered.

        The ``data_dict`` contains: ``resource_view``, ``resource`` and
        ``package``.
        '''

    def form_template(self, context, data_dict):
        '''
        Returns a string representing the location of the template to be
        rendered for the read page.

        The ``data_dict`` contains: ``resource_view``, ``resource`` and
        ``package``.
        '''

class IResourcePreview(Interface):
    ''' For backwards compatibility with the old resource preview code. '''
    def can_preview(self, data_dict):
        '''Return info on whether the plugin can preview the resource.

        This can be done in two ways:

        1. The old way is to just return ``True`` or ``False``.

        2. The new way is to return a dict with  three keys:

           ``'can_preview'`` (``boolean``)
             ``True`` if the extension can preview the resource.

           ``'fixable'`` (``string``)
             A string explaining how preview for the resource could be enabled,
             for example if the ``resource_proxy`` plugin was enabled.

           ``'quality'`` (``int``)
             How good the preview is: ``1`` (poor), ``2`` (average) or
             ``3`` (good). When multiple preview extensions can preview the
             same resource, this is used to determine which extension will
             be used.

        :param data_dict: the resource to be previewed and the dataset that it
          belongs to.
        :type data_dict: dictionary

        Make sure to check the ``on_same_domain`` value of the resource or the
        url if your preview requires the resource to be on the same domain
        because of the same-origin policy.  To find out how to preview
        resources that are on a different domain, read :ref:`resource-proxy`.

        '''

    def setup_template_variables(self, context, data_dict):
        '''
        Add variables to c just prior to the template being rendered.
        The ``data_dict`` contains the resource and the package.

        Change the url to a proxied domain if necessary.
        '''

    def preview_template(self, context, data_dict):
        '''
        Returns a string representing the location of the template to be
        rendered for the read page.
        The ``data_dict`` contains the resource and the package.
        '''

class ITagController(Interface):
    '''
    Hook into the Tag controller. These will usually be called just before
    committing or returning the respective object, i.e. all validation,
    synchronization and authorization setup are complete.

    '''
    def before_view(self, tag_dict):
        '''
        Extensions will recieve this before the tag gets displayed. The
        dictionary passed will be the one that gets sent to the template.

        '''
        return tag_dict


class IGroupController(Interface):
    """
    Hook into the Group controller. These will
    usually be called just before committing or returning the
    respective object, i.e. all validation, synchronization
    and authorization setup are complete.
    """

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def before_view(self, pkg_dict):
        '''
             Extensions will recieve this before the group gets
             displayed. The dictionary passed will be the one that gets
             sent to the template.
        '''
        return pkg_dict


class IOrganizationController(Interface):
    """
    Hook into the Organization controller. These will
    usually be called just before committing or returning the
    respective object, i.e. all validation, synchronization
    and authorization setup are complete.
    """

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def before_view(self, pkg_dict):
        '''
             Extensions will recieve this before the organization gets
             displayed. The dictionary passed will be the one that gets
             sent to the template.
        '''
        return pkg_dict


class IPackageController(Interface):
    """
    Hook into the package controller.
    (see IGroupController)
    """

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def after_create(self, context, pkg_dict):
        '''
            Extensions will receive the validated data dict after the package
            has been created (Note that the create method will return a package
            domain object, which may not include all fields). Also the newly
            created package id will be added to the dict.
        '''
        pass

    def after_update(self, context, pkg_dict):
        '''
            Extensions will receive the validated data dict after the package
            has been updated (Note that the edit method will return a package
            domain object, which may not include all fields).
        '''
        pass

    def after_delete(self, context, pkg_dict):
        '''
            Extensions will receive the data dict (tipically containing
            just the package id) after the package has been deleted.
        '''
        pass

    def after_show(self, context, pkg_dict):
        '''
            Extensions will receive the validated data dict after the package
            is ready for display (Note that the read method will return a
            package domain object, which may not include all fields).
        '''
        pass

    def before_search(self, search_params):
        '''
            Extensions will receive a dictionary with the query parameters,
            and should return a modified (or not) version of it.

            search_params will include an `extras` dictionary with all values
            from fields starting with `ext_`, so extensions can receive user
            input from specific fields.

        '''
        return search_params

    def after_search(self, search_results, search_params):
        '''
            Extensions will receive the search results, as well as the search
            parameters, and should return a modified (or not) object with the
            same structure:

                {'count': '', 'results': '', 'facets': ''}

            Note that count and facets may need to be adjusted if the extension
            changed the results for some reason.

            search_params will include an `extras` dictionary with all values
            from fields starting with `ext_`, so extensions can receive user
            input from specific fields.

        '''

        return search_results

    def before_index(self, pkg_dict):
        '''
             Extensions will receive what will be given to the solr for
             indexing. This is essentially a flattened dict (except for
             multli-valued fields such as tags) of all the terms sent to
             the indexer. The extension can modify this by returning an
             altered version.
        '''
        return pkg_dict

    def before_view(self, pkg_dict):
        '''
             Extensions will recieve this before the dataset gets
             displayed. The dictionary passed will be the one that gets
             sent to the template.
        '''
        return pkg_dict


class IResourceController(Interface):
    """
    Hook into the resource controller.
    """

    def before_create(self, context, resource):
        """
        Extensions will receive this before a resource is created.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the resource to be added
            to the dataset (the one that is about to be created).
        :type resource: dictionary
        """
        pass

    def after_create(self, context, resource):
        """
        Extensions will receive this after a resource is created.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the latest resource added
            to the dataset (the one that was just created). A key in the
            resource dictionary worth mentioning is ``url_type`` which is
            set to ``upload`` when the resource file is uploaded instead
            of linked.
        :type resource: dictionary
        """
        pass

    def before_update(self, context, current, resource):
        """
        Extensions will receive this before a resource is updated.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param current: The current resource which is about to be updated
        :type current: dictionary
        :param resource: An object representing the updated resource which
            will replace the ``current`` one.
        :type resource: dictionary
        """
        pass

    def after_update(self, context, resource):
        """
        Extensions will receive this after a resource is updated.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the updated resource in
            the dataset (the one that was just updated). As with
            ``after_create``, a noteworthy key in the resource dictionary
            ``url_type`` which is set to ``upload`` when the resource file
            is uploaded instead of linked.
        :type resource: dictionary
        """
        pass

    def before_delete(self, context, resource, resources):
        """
        Extensions will receive this before a previously created resource is
        deleted.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resource: An object representing the resource that is about
            to be deleted. This is a dictionary with one key: ``id`` which
            holds the id ``string`` of the resource that should be deleted.
        :type resource: dictionary
        :param resources: The list of resources from which the resource will
            be deleted (including the resource to be deleted if it existed
            in the package).
        :type resources: list
        """
        pass

    def after_delete(self, context, resources):
        """
        Extensions will receive this after a previously created resource is
        deleted.

        :param context: The context object of the current request, this
            includes for example access to the ``model`` and the ``user``.
        :type context: dictionary
        :param resources: A list of objects representing the remaining
            resources after a resource has been removed.
        :type resource: list
        """
        pass

    def before_show(self, resource_dict):
        '''
        Extensions will receive the validated data dict before the resource
        is ready for display.

        Be aware that this method is not only called for UI display, but also
        in other methods like when a resource is deleted because showing a
        package is used to get access to the resources in a package.
        '''
        return resource_dict


class IPluginObserver(Interface):
    """
    Plugin to the plugin loading mechanism
    """

    def before_load(self, plugin):
        """
        Called before a plugin is loaded
        This method is passed the plugin class.
        """

    def after_load(self, service):
        """
        Called after a plugin has been loaded.
        This method is passed the instantiated service object.
        """

    def before_unload(self, plugin):
        """
        Called before a plugin is loaded
        This method is passed the plugin class.
        """

    def after_unload(self, service):
        """
        Called after a plugin has been unloaded.
        This method is passed the instantiated service object.
        """


class IConfigurable(Interface):
    """
    Pass configuration to plugins and extensions
    """

    def configure(self, config):
        """
        Called by load_environment
        """


class IConfigurer(Interface):
    """
    Configure CKAN (pylons) environment via the ``pylons.config`` object
    """

    def update_config(self, config):
        """
        Called by load_environment at earliest point when config is
        available to plugins. The config should be updated in place.

        :param config: ``pylons.config`` object
        """


class IActions(Interface):
    """
    Allow adding of actions to the logic layer.
    """
    def get_actions(self):
        """
        Should return a dict, the keys being the name of the logic
        function and the values being the functions themselves.

        By decorating a function with the `ckan.logic.side_effect_free`
        decorator, the associated action will be made available by a GET
        request (as well as the usual POST request) through the action API.
        """


class IValidators(Interface):
    """
    Add extra validators to be returned by
    :py:func:`ckan.plugins.toolkit.get_validator`.
    """
    def get_validators(self):
        """Return the validator functions provided by this plugin.

        Return a dictionary mapping validator names (strings) to
        validator functions. For example::

            {'valid_shoe_size': shoe_size_validator,
             'valid_hair_color': hair_color_validator}

        These validator functions would then be available when a
        plugin calls :py:func:`ckan.plugins.toolkit.get_validator`.
        """


class IAuthFunctions(Interface):
    '''Override CKAN's authorization functions, or add new auth functions.'''

    def get_auth_functions(self):
        '''Return the authorization functions provided by this plugin.

        Return a dictionary mapping authorization function names (strings) to
        functions. For example::

            {'user_create': my_custom_user_create_function,
             'group_create': my_custom_group_create}

        When a user tries to carry out an action via the CKAN API or web
        interface and CKAN or a CKAN plugin calls
        ``check_access('some_action')`` as a result, an authorization function
        named ``'some_action'`` will be searched for in the authorization
        functions registered by plugins and in CKAN's core authorization
        functions (found in ``ckan/logic/auth/``).

        For example when a user tries to create a package, a
        ``'package_create'`` authorization function is searched for.

        If an extension registers an authorization function with the same name
        as one of CKAN's default authorization functions (as with
        ``'user_create'`` and ``'group_create'`` above), the extension's
        function will override the default one.

        Each authorization function should take two parameters ``context`` and
        ``data_dict``, and should return a dictionary ``{'success': True}`` to
        authorize the action or ``{'success': False}`` to deny it, for
        example::

            def user_create(context, data_dict=None):
                if (some condition):
                    return {'success': True}
                else:
                    return {'success': False, 'msg': 'Not allowed to register'}

        The context object will contain a ``model`` that can be used to query
        the database, a ``user`` containing the name of the user doing the
        request (or their IP if it is an anonymous web request) and an
        ``auth_user_obj`` containing the actual model.User object (or None if
        it is an anonymous request).

        See ``ckan/logic/auth/`` for more examples.

        Note that by default, all auth functions provided by extensions are assumed
        to require a validated user or API key, otherwise a
        :py:class:`ckan.logic.NotAuthorized`: exception will be raised. This check
        will be performed *before* calling the actual auth function. If you want
        to allow anonymous access to one of your actions, its auth function must
        be decorated with the ``auth_allow_anonymous_access`` decorator, available
        on the plugins toolkit.

        For example::

            import ckan.plugins as p

            @p.toolkit.auth_allow_anonymous_access
            def my_search_action(context, data_dict):
                # Note that you can still return {'success': False} if for some
                # reason access is denied.

            def my_create_action(context, data_dict):
                # Unless there is a logged in user or a valid API key provided
                # NotAuthorized will be raised before reaching this function.

        '''


class ITemplateHelpers(Interface):
    '''Add custom template helper functions.

    By implementing this plugin interface plugins can provide their own
    template helper functions, which custom templates can then access via the
    ``h`` variable.

    See ``ckanext/example_itemplatehelpers`` for an example plugin.

    '''
    def get_helpers(self):
        '''Return a dict mapping names to helper functions.

        The keys of the dict should be the names with which the helper
        functions will be made available to templates, and the values should be
        the functions themselves. For example, a dict like:
        ``{'example_helper': example_helper}`` allows templates to access the
        ``example_helper`` function via ``h.example_helper()``.

        Function names should start with the name of the extension providing
        the function, to prevent name clashes between extensions.

        '''


class IDatasetForm(Interface):
    '''Customize CKAN's dataset (package) schemas and forms.

    By implementing this interface plugins can customise CKAN's dataset schema,
    for example to add new custom fields to datasets.

    Multiple IDatasetForm plugins can be used at once, each plugin associating
    itself with different package types using the ``package_types()`` and
    ``is_fallback()`` methods below, and then providing different schemas and
    templates for different types of dataset.  When a package controller action
    is invoked, the ``type`` field of the package will determine which
    IDatasetForm plugin (if any) gets delegated to.

    When implementing IDatasetForm, you can inherit from
    ``ckan.plugins.toolkit.DefaultDatasetForm``, which provides default
    implementations for each of the methods defined in this interface.

    See ``ckanext/example_idatasetform`` for an example plugin.

    '''
    def package_types(self):
        '''Return an iterable of package types that this plugin handles.

        If a request involving a package of one of the returned types is made,
        then this plugin instance will be delegated to.

        There cannot be two IDatasetForm plugins that return the same package
        type, if this happens then CKAN will raise an exception at startup.

        :rtype: iterable of strings

        '''

    def is_fallback(self):
        '''Return ``True`` if this plugin is the fallback plugin.

        When no IDatasetForm plugin's ``package_types()`` match the ``type`` of
        the package being processed, the fallback plugin is delegated to
        instead.

        There cannot be more than one IDatasetForm plugin whose
        ``is_fallback()`` method returns ``True``, if this happens CKAN will
        raise an exception at startup.

        If no IDatasetForm plugin's ``is_fallback()`` method returns ``True``,
        CKAN will use ``DefaultDatasetForm`` as the fallback.

        :rtype: boolean

        '''

    def create_package_schema(self):
        '''Return the schema for validating new dataset dicts.

        CKAN will use the returned schema to validate and convert data coming
        from users (via the dataset form or API) when creating new datasets,
        before entering that data into the database.

        If it inherits from ``ckan.plugins.toolkit.DefaultDatasetForm``, a
        plugin can call ``DefaultDatasetForm``'s ``create_package_schema()``
        method to get the default schema and then modify and return it.

        CKAN's ``convert_to_tags()`` or ``convert_to_extras()`` functions can
        be used to convert custom fields into dataset tags or extras for
        storing in the database.

        See ``ckanext/example_idatasetform`` for examples.

        :returns: a dictionary mapping dataset dict keys to lists of validator
          and converter functions to be applied to those keys
        :rtype: dictionary

        '''

    def update_package_schema(self):
        '''Return the schema for validating updated dataset dicts.

        CKAN will use the returned schema to validate and convert data coming
        from users (via the dataset form or API) when updating datasets, before
        entering that data into the database.

        If it inherits from ``ckan.plugins.toolkit.DefaultDatasetForm``, a
        plugin can call ``DefaultDatasetForm``'s ``update_package_schema()``
        method to get the default schema and then modify and return it.

        CKAN's ``convert_to_tags()`` or ``convert_to_extras()`` functions can
        be used to convert custom fields into dataset tags or extras for
        storing in the database.

        See ``ckanext/example_idatasetform`` for examples.

        :returns: a dictionary mapping dataset dict keys to lists of validator
          and converter functions to be applied to those keys
        :rtype: dictionary

        '''

    def show_package_schema(self):
        '''
        Return a schema to validate datasets before they're shown to the user.

        CKAN will use the returned schema to validate and convert data coming
        from the database before it is returned to the user via the API or
        passed to a template for rendering.

        If it inherits from ``ckan.plugins.toolkit.DefaultDatasetForm``, a
        plugin can call ``DefaultDatasetForm``'s ``show_package_schema()``
        method to get the default schema and then modify and return it.

        If you have used ``convert_to_tags()`` or ``convert_to_extras()`` in
        your ``create_package_schema()`` and ``update_package_schema()`` then
        you should use ``convert_from_tags()`` or ``convert_from_extras()`` in
        your ``show_package_schema()`` to convert the tags or extras in the
        database back into your custom dataset fields.

        See ``ckanext/example_idatasetform`` for examples.

        :returns: a dictionary mapping dataset dict keys to lists of validator
          and converter functions to be applied to those keys
        :rtype: dictionary

        '''

    def setup_template_variables(self, context, data_dict):
        '''Add variables to the template context for use in templates.

        This function is called before a dataset template is rendered. If you
        have custom dataset templates that require some additional variables,
        you can add them to the template context ``ckan.plugins.toolkit.c``
        here and they will be available in your templates. See
        ``ckanext/example_idatasetform`` for an example.

        '''

    def new_template(self):
        '''Return the path to the template for the new dataset page.

        The path should be relative to the plugin's templates dir, e.g.
        ``'package/new.html'``.

        :rtype: string

        '''

    def read_template(self):
        '''Return the path to the template for the dataset read page.

        The path should be relative to the plugin's templates dir, e.g.
        ``'package/read.html'``.

        If the user requests the dataset in a format other than HTML
        (CKAN supports returning datasets in RDF/XML or N3 format by appending
        .rdf or .n3 to the dataset read URL, see
        :doc:`/maintaining/linked-data-and-rdf`) then CKAN will try to render a
        template file with the same path as returned by this function, but a
        different filename extension, e.g. ``'package/read.rdf'``.  If your
        extension doesn't have this RDF version of the template file, the user
        will get a 404 error.

        :rtype: string

        '''

    def edit_template(self):
        '''Return the path to the template for the dataset edit page.

        The path should be relative to the plugin's templates dir, e.g.
        ``'package/edit.html'``.

        :rtype: string

        '''

    def search_template(self):
        '''Return the path to the template for use in the dataset search page.

        This template is used to render each dataset that is listed in the
        search results on the dataset search page.

        The path should be relative to the plugin's templates dir, e.g.
        ``'package/search.html'``.

        :rtype: string

        '''

    def history_template(self):
        '''Return the path to the template for the dataset history page.

        The path should be relative to the plugin's templates dir, e.g.
        ``'package/history.html'``.

        :rtype: string

        '''

    def resource_template(self):
        '''Return the path to the template for the resource read page.

        The path should be relative to the plugin's templates dir, e.g.
        ``'package/resource_read.html'``.

        :rtype: string

        '''

    def package_form(self):
        '''Return the path to the template for the dataset form.

        The path should be relative to the plugin's templates dir, e.g.
        ``'package/form.html'``.

        :rtype: string

        '''

    def resource_form(self):
        '''Return the path to the template for the resource form.

        The path should be relative to the plugin's templates dir, e.g.
        ``'package/snippets/resource_form.html'``

        :rtype: string
        '''

    def validate(self, context, data_dict, schema, action):
        """Customize validation of datasets.

        When this method is implemented it is used to perform all validation
        for these datasets. The default implementation calls and returns the
        result from ``ckan.plugins.toolkit.navl_validate``.

        This is an adavanced interface. Most changes to validation should be
        accomplished by customizing the schemas returned from
        ``show_package_schema()``, ``create_package_schema()``
        and ``update_package_schama()``. If you need to have a different
        schema depending on the user or value of any field stored in the
        dataset, or if you wish to use a different method for validation, then
        this method may be used.

        :param context: extra information about the request
        :type context: dictionary
        :param data_dict: the dataset to be validated
        :type data_dict: dictionary
        :param schema: a schema, typically from ``show_package_schema()``,
          ``create_package_schema()`` or ``update_package_schama()``
        :type schema: dictionary
        :param action: ``'package_show'``, ``'package_create'`` or
          ``'package_update'``
        :type action: string
        :returns: (data_dict, errors) where data_dict is the possibly-modified
          dataset and errors is a dictionary with keys matching data_dict
          and lists-of-string-error-messages as values
        :rtype: (dictionary, dictionary)
        """


class IGroupForm(Interface):
    """
    Allows customisation of the group controller as a plugin.

    The behaviour of the plugin is determined by 5 method hooks:

     - package_form(self)
     - form_to_db_schema(self)
     - db_to_form_schema(self)
     - check_data_dict(self, data_dict)
     - setup_template_variables(self, context, data_dict)

    Furthermore, there can be many implementations of this plugin registered
    at once.  With each instance associating itself with 0 or more group
    type strings.  When a group controller action is invoked, the group
    type determines which of the registered plugins to delegate to.  Each
    implementation must implement two methods which are used to determine the
    group-type -> plugin mapping:

     - is_fallback(self)
     - group_types(self)

    Implementations might want to consider mixing in
    ckan.lib.plugins.DefaultGroupForm which provides
    default behaviours for the 5 method hooks.

    """

    ##### These methods control when the plugin is delegated to          #####

    def is_fallback(self):
        """
        Returns true if this provides the fallback behaviour, when no other
        plugin instance matches a group's type.

        There must be exactly one fallback controller defined, any attempt to
        register more than one will throw an exception at startup.  If there's
        no fallback registered at startup the
        ckan.lib.plugins.DefaultGroupForm used as the fallback.
        """

    def group_types(self):
        """
        Returns an iterable of group type strings.

        If a request involving a group of one of those types is made, then
        this plugin instance will be delegated to.

        There must only be one plugin registered to each group type.  Any
        attempts to register more than one plugin instance to a given group
        type will raise an exception at startup.
        """

    ##### End of control methods

    ##### Hooks for customising the PackageController's behaviour        #####
    ##### TODO: flesh out the docstrings a little more.                  #####
    def new_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the 'new' page. Uses the default_group_type configuration
        option to determine which plugin to use the template from.
        """

    def index_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the index page. Uses the default_group_type configuration
        option to determine which plugin to use the template from.
        """

    def read_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the read page
        """

    def history_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the history page
        """

    def edit_template(self):
        """
        Returns a string representing the location of the template to be
        rendered for the edit page
        """

    def package_form(self):
        """
        Returns a string representing the location of the template to be
        rendered.  e.g. "group/new_group_form.html".
        """

    def form_to_db_schema(self):
        """
        Returns the schema for mapping group data from a form to a format
        suitable for the database.
        """

    def db_to_form_schema(self):
        """
        Returns the schema for mapping group data from the database into a
        format suitable for the form (optional)
        """

    def check_data_dict(self, data_dict):
        """
        Check if the return data is correct.

        raise a DataError if not.
        """

    def setup_template_variables(self, context, data_dict):
        """
        Add variables to c just prior to the template being rendered.
        """

    def validate(self, context, data_dict, schema, action):
        """Customize validation of groups.

        When this method is implemented it is used to perform all validation
        for these groups. The default implementation calls and returns the
        result from ``ckan.plugins.toolkit.navl_validate``.

        This is an adavanced interface. Most changes to validation should be
        accomplished by customizing the schemas returned from
        ``form_to_db_schema()`` and ``db_to_form_schema()``
        If you need to have a different
        schema depending on the user or value of any field stored in the
        group, or if you wish to use a different method for validation, then
        this method may be used.

        :param context: extra information about the request
        :type context: dictionary
        :param data_dict: the group to be validated
        :type data_dict: dictionary
        :param schema: a schema, typically from ``form_to_db_schema()``,
          or ``db_to_form_schama()``
        :type schema: dictionary
        :param action: ``'group_show'``, ``'group_create'``,
          ``'group_update'``, ``'organization_show'``,
          ``'organization_create'`` or ``'organization_update'``
        :type action: string
        :returns: (data_dict, errors) where data_dict is the possibly-modified
          group and errors is a dictionary with keys matching data_dict
          and lists-of-string-error-messages as values
        :rtype: (dictionary, dictionary)
        """

    ##### End of hooks                                                   #####

class IFacets(Interface):
    '''Customize the search facets shown on search pages.

    By implementing this interface plugins can customize the search facets that
    are displayed for filtering search results on the dataset search page,
    organization pages and group pages.

    The ``facets_dict`` passed to each of the functions below is an
    ``OrderedDict`` in which the keys are CKAN's internal names for the facets
    and the values are the titles that will be shown for the facets in the web
    interface. The order of the keys in the dict determine the order that
    facets appear in on the page.  For example::

        {'groups': _('Groups'),
         'tags': _('Tags'),
         'res_format': _('Formats'),
         'license': _('License')}

    To preserve ordering, make sure to add new facets to the existing dict
    rather than updating it, ie do this::

        facets_dict['groups'] = p.toolkit._('Publisher')
        facets_dict['secondary_publisher'] = p.toolkit._('Secondary Publisher')

    rather than this::

        facets_dict.update({
           'groups': p.toolkit._('Publisher'),
           'secondary_publisher': p.toolkit._('Secondary Publisher'),
        })

    Dataset searches can be faceted on any field in the dataset schema that it
    makes sense to facet on. This means any dataset field that is in CKAN's
    Solr search index, basically any field that you see returned by
    :py:func:`~ckan.logic.action.get.package_show`.

    If there are multiple ``IFacets`` plugins active at once, each plugin will
    be called (in the order that they're listed in the CKAN config file) and
    they will each be able to modify the facets dict in turn.

    '''
    def dataset_facets(self, facets_dict, package_type):
        '''Modify and return the ``facets_dict`` for the dataset search page.

        The ``package_type`` is the type of package that these facets apply to.
        Plugins can provide different search facets for different types of
        package. See :py:class:`~ckan.plugins.interfaces.IDatasetForm`.

        :param facets_dict: the search facets as currently specified
        :type facets_dict: OrderedDict

        :param package_type: the package type that these facets apply to
        :type package_type: string

        :returns: the updated ``facets_dict``
        :rtype: OrderedDict

        '''
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        '''Modify and return the ``facets_dict`` for a group's page.

        The ``package_type`` is the type of package that these facets apply to.
        Plugins can provide different search facets for different types of
        package. See :py:class:`~ckan.plugins.interfaces.IDatasetForm`.

        The ``group_type`` is the type of group that these facets apply to.
        Plugins can provide different search facets for different types of
        group. See :py:class:`~ckan.plugins.interfaces.IGroupForm`.

        :param facets_dict: the search facets as currently specified
        :type facets_dict: OrderedDict

        :param group_type: the group type that these facets apply to
        :type group_type: string

        :param package_type: the package type that these facets apply to
        :type package_type: string

        :returns: the updated ``facets_dict``
        :rtype: OrderedDict

        '''
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        '''Modify and return the ``facets_dict`` for an organization's page.

        The ``package_type`` is the type of package that these facets apply to.
        Plugins can provide different search facets for different types of
        package. See :py:class:`~ckan.plugins.interfaces.IDatasetForm`.

        The ``organization_type`` is the type of organization that these facets
        apply to.  Plugins can provide different search facets for different
        types of organization. See
        :py:class:`~ckan.plugins.interfaces.IGroupForm`.

        :param facets_dict: the search facets as currently specified
        :type facets_dict: OrderedDict

        :param organization_type: the organization type that these facets apply
                                  to
        :type organization_type: string

        :param package_type: the package type that these facets apply to
        :type package_type: string

        :returns: the updated ``facets_dict``
        :rtype: OrderedDict

        '''
        return facets_dict


class IAuthenticator(Interface):
    '''EXPERIMENTAL

    Allows custom authentication methods to be integrated into CKAN.
    Currently it is experimental and the interface may change.'''


    def identify(self):
        '''called to identify the user.

        If the user is identfied then it should set
        c.user: The id of the user
        c.userobj: The actual user object (this may be removed as a
        requirement in a later release so that access to the model is not
        required)
        '''

    def login(self):
        '''called at login.'''

    def logout(self):
        '''called at logout.'''

    def abort(self, status_code, detail, headers, comment):
        '''called on abort.  This allows aborts due to authorization issues
        to be overriden'''
        return (status_code, detail, headers, comment)
