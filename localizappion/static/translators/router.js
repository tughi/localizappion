define(['knockout', 'crossroads', 'hasher'], function(ko, crossroads, hasher) {
    'use strict';

    function Router(config) {
        this.currentRoute = ko.observable({});

        ko.utils.arrayForEach(config.routes, route => {
            crossroads.addRoute(route.url, params => {
                this.currentRoute(ko.utils.extend(params, route.params));
            });
        });
    }

    var router = new Router({
        routes: [
            { url: 'translate', params: { page: 'translate' } },
            { url: 'translate/{stringName}', params: { page: 'translate' } },
            { url: '{url*}', params: { page: null } }
        ]
    });

    function onHashChanged(hash) {
        if (hash === '') {
            hasher.setHash('translate');
        } else {
            crossroads.parse(hash);
        }
    }

    crossroads.normalizeFn = crossroads.NORM_AS_OBJECT;
    hasher.initialized.add(onHashChanged);
    hasher.changed.add(onHashChanged);
    hasher.init();

    return router;
});
