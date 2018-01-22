define(['knockout', 'crossroads', 'hasher'], function (ko, crossroads, hasher) {
    'use strict';

    function Router(config) {
        this.currentRoute = ko.observable({});

        ko.utils.arrayForEach(config.routes, route => {
            crossroads.addRoute(route.url, params => {
                this.currentRoute(ko.utils.extend(params, route.params));
            });
        });
    };

    var router = new Router({
        routes: [
            { url: 'projects/{projectId}', params: { page: 'project-detail' } },
            { url: 'projects/{projectId}/screenshots', params: { page: 'project-screenshots' } },
            { url: 'projects/{projectId}/screenshots/new/{name}', params: { page: 'project-screenshot' } },
            { url: 'projects/{projectId}/screenshots/{screenshotId}', params: { page: 'project-screenshot' } },
            { url: 'projects/{projectId}/strings', params: { page: 'project-strings' } },
            // { url: 'projects/{projectId}/translations', params: { page: 'project-translations' } },
            { url: '{url*}', params: { page: null } },
        ]
    });

    crossroads.normalizeFn = crossroads.NORM_AS_OBJECT;
    hasher.initialized.add(hash => crossroads.parse(hash));
    hasher.changed.add(hash => {
        crossroads.parse(hash);
    });
    hasher.init();

    return router;
});
