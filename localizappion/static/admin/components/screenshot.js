define(['jquery', 'knockout', 'text!./screenshot.html'], function ($, ko, template) {
    'use strict';

    ko.bindingHandlers.dropZone = {
        init: function (element, valueAccessor) {
            const url = valueAccessor();
            if (typeof url !== 'function') {
                return;
            }

            function onDragLeave(event) {
                event.preventDefault();

                $(element).removeClass('drop-zone');
            };

            function onDragOver(event) {
                event.preventDefault();

                $(element).addClass('drop-zone');
            };

            function onDrop(event) {
                event.preventDefault();

                $(element).removeClass('drop-zone');

                const dataTransfer = event.originalEvent.dataTransfer;
                let imageFile = null;
                if (dataTransfer.items) {
                    for (let i = 0; i < dataTransfer.items.length; i++) {
                        let item = dataTransfer.items[i];
                        if (item.kind === 'file') {
                            let file = item.getAsFile();
                            if (file.type.startsWith('image/png')) {
                                imageFile = file;
                                break;
                            }
                        }
                    }
                } else {
                    for (let i = 0; i < dataTransfer.files.length; i++) {
                        let file = dataTransfer.files[i];
                        if (file.type.startsWith('image/png')) {
                            imageFile = file;
                        }
                    }
                }

                if (imageFile) {
                    let reader = new FileReader();
                    reader.onload = function (event) {
                        url(event.target.result);
                    };
                    reader.readAsDataURL(imageFile);
                }
            };

            $(element).on({
                dragexit: onDragLeave,
                dragleave: onDragLeave,
                dragover: onDragOver,
                drop: onDrop,
            });
        }
    };

    function Screenshot(params) {
        this.url = typeof params.url === 'function' ? params.url : ko.observable(params.url);
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
