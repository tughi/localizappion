define(['knockout', 'text!./screenshot.html'], function (ko, template) {
    'use strict';

    function Screenshot(params) {
        this.url = params.url;
        this.screenshotStrings = (params.screenshotStrings || []).map(screenshotString => new ScreenshotString(screenshotString));
        this.activeScreenshotString = params.activeScreenshotString;
        this.hoveredScreenshotString = params.hoveredScreenshotString;
    }

    function ScreenshotString(data) {
        this.area = ko.observable(data.area);
        this.string = data.string;
        this.areaStyle = ko.computed(function () {
            var match = this.area().match(/\(([0-9.]+),([0-9.]+)\)x\(([0-9.]+),([0-9.]+)\)/);
            if (match) {
                return `left: ${match[1]}%; top: ${match[2]}%; right: ${100 - match[3]}%; bottom: ${100 - match[4]}%;`;
            }
        }, this);
    }

    return {
        template,
        viewModel: Screenshot
    }
});
