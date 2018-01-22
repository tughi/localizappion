define(['jquery', 'knockout', 'text!./screenshot.html'], function ($, ko, template) {
    'use strict';

    ko.bindingHandlers.dropZone = {
        init: function (element, valueAccessor) {
            const url = valueAccessor();
            if (!ko.isObservable(url)) {
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

    ko.bindingHandlers.areaEditor = {
        init: function (element, valueAccessor) {
            const activeScreenshotString = valueAccessor();
            if (!ko.isObservable(activeScreenshotString)) {
                return;
            }

            let activeArea = null;
            let mouseDownX, mouseDownY;
            let mouseMoveX, mouseMoveY;

            const $element = $(element);
            $element.on({
                mousedown: function (event) {
                    event.preventDefault();
                    
                    activeArea = activeScreenshotString() && activeScreenshotString().area;
                    if (activeArea) {
                        mouseDownX = event.offsetX;
                        mouseDownY = event.offsetY;
                    }
                },
                mousemove: function (event) {
                    if (activeArea) {
                        mouseMoveX = event.offsetX;
                        mouseMoveY = event.offsetY;
                        
                        let screenshotWidth = $element.width();
                        let screenshotHeight = $element.height();
                        
                        let x1 = (Math.min(mouseDownX, mouseMoveX) * 100. / screenshotWidth).toFixed(2);
                        let y1 = (Math.min(mouseDownY, mouseMoveY) * 100. / screenshotHeight).toFixed(2);
                        let x2 = (Math.max(mouseDownX, mouseMoveX) * 100. / screenshotWidth).toFixed(2);
                        let y2 = (Math.max(mouseDownY, mouseMoveY) * 100. / screenshotHeight).toFixed(2);
                        activeArea(`(${x1},${y1})x(${x2},${y2})`);
                    }
                },
                mouseleave: function (event) {
                    activeArea = null;
                },
                mouseup: function (event) {
                    activeArea = null;
                }
            });            
        }
    };

    function Screenshot(params) {
        this.editable = params.editable;
        this.url = ko.isObservable(params.url) ? params.url : ko.observable(params.url);
        this.activeScreenshotString = params.activeScreenshotString;
        this.screenshotStrings = ko.computed(() => {
            const screenshotStrings = ko.unwrap(params.screenshotStrings);
            const activeScreenshotString = params.activeScreenshotString && params.activeScreenshotString();
            const hoveredScreenshotString = params.hoveredScreenshotString && params.hoveredScreenshotString();
            return ko.utils.arrayMap(screenshotStrings, screenshotString => {
                return new ScreenshotString(ko.utils.extend(
                    {
                        active: activeScreenshotString == screenshotString,
                        hovered: hoveredScreenshotString == screenshotString
                    },
                    screenshotString
                ));
            });
        });
    }

    function ScreenshotString(data) {
        this.area = data.area;
        this.string = data.string;
        this.active = data.active;
        this.hovered = data.hovered;

        this.areaStyle = ko.computed(function () {
            var match = ko.unwrap(this.area).match(/\(([0-9.]+),([0-9.]+)\)x\(([0-9.]+),([0-9.]+)\)/);
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
