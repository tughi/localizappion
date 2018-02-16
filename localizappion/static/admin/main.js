require.config({
    baseUrl: 'static/admin',
    paths: {
        'bootstrap': 'https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0/js/bootstrap.min',
        'crossroads': 'https://cdnjs.cloudflare.com/ajax/libs/crossroads/0.12.2/crossroads.min',
        'hasher': 'https://cdnjs.cloudflare.com/ajax/libs/hasher/1.2.0/hasher.min',
        'jquery': 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min',
        'knockout': 'https://cdnjs.cloudflare.com/ajax/libs/knockout/3.4.2/knockout-min',
        'popper': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.13.0/umd/popper.min',
        'signals': 'https://cdnjs.cloudflare.com/ajax/libs/js-signals/1.0.0/js-signals.min',
        'text': 'https://cdnjs.cloudflare.com/ajax/libs/require-text/2.0.12/text.min'
    },
    shim: {
        'bootstrap': {
            deps: ['jquery', 'popper']
        }
    },
    map: {
        'bootstrap': {
            'popper.js': 'popper'
        }
    }
});

require(['jquery', 'knockout', 'router', 'bootstrap'], function ($, ko, router) {
    $('html').on('dragover drop', event => {
        event.preventDefault();
    });

    ko.components.register('modal', { require: 'components/modal' });
    ko.components.register('navigation-bar', { require: 'components/navigation-bar' });
    ko.components.register('project-create', { require: 'components/project-create' });
    ko.components.register('project-detail', { require: 'components/project-detail' });
    ko.components.register('project-screenshot', { require: 'components/project-screenshot' });
    ko.components.register('project-screenshots', { require: 'components/project-screenshots' });
    ko.components.register('project-strings', { require: 'components/project-strings' });
    ko.components.register('screenshot', { require: 'components/screenshot' });

    ko.applyBindings({ route: router.currentRoute });
});
