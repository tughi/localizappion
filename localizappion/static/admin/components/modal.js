define(['jquery', 'knockout', 'text!./modal.html'], function ($, ko, template) {
    'use strict';

    ko.bindingHandlers.modal = {
        init: function (element, valueAccessor) {
            $(element).modal({ show: false });
            $(element).on('shown.bs.modal', event => {
                $(element).find('input').first().trigger('focus');
            });

            const value = valueAccessor();
            if (ko.isObservable(value)) {
                $(element).on('hidden.bs.modal', event => value(false));
            }
        },
        update: function (element, valueAccessor) {
            const value = valueAccessor();
            $(element).modal(ko.unwrap(value) ? 'show' : 'hide');
        }
    };

    function ViewModel(params) {
        this.title = params.title;
        this.trigger = params.trigger;
        this.data = params.data;
    }

    return {
        template,
        viewModel: ViewModel
    }
});
