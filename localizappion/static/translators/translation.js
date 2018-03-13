define(['jquery', 'knockout'], function($, ko) {
    'use strict';

    function Translation() {
        this.loaded = false;

        this.project = ko.observable();
        this.language = ko.observable();
        this.strings = ko.observable();

        this.set = (data) => {
            this.project(data.project);
            this.language(data.language);
            this.strings(data.strings);
            this.loaded = true;
        };

        $.get({
            url:'get-translation',
            success: (data) => {
                this.set(data);
            }
        });
    }

    return new Translation();
});