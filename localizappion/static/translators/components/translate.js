define(['jquery', 'hasher', 'knockout', 'text!./translate.html', 'translation', '../utils/html'], function($, hasher, ko, template, translation, html) {
    'use strict';

    function findTranslatableString(strings) {
        return strings.find(string => {
            let suggestions = string.suggestions;
            if (suggestions) {
                let votedSuggestion = suggestions.find(suggestion => suggestion.voted);
                return !votedSuggestion;
            }
            return false;
        });
    }

    function ViewModel(params) {
        this.translation = translation;
        this.string = ko.observable();
        this.stringIndex = -1;
        this.votedSuggestion = ko.observable();
        this.newSuggestionZero = ko.observable('');
        this.newSuggestionOne = ko.observable('');
        this.newSuggestionTwo = ko.observable('');
        this.newSuggestionFew = ko.observable('');
        this.newSuggestionMany = ko.observable('');
        this.newSuggestionOther = ko.observable('');
        this.newSuggestion = {
            zero: this.newSuggestionZero,
            one: this.newSuggestionOne,
            two: this.newSuggestionTwo,
            few: this.newSuggestionFew,
            many: this.newSuggestionMany,
            other: this.newSuggestionOther
        };

        this.onTranslationLoaded = () => {
            let strings = this.translation.strings();
            let stringName = params.stringName;
            let stringIndex = strings.findIndex(string => string.name === stringName);
            if (stringIndex >= 0) {
                let string = strings[stringIndex];
                this.string(string);
                this.stringIndex = stringIndex;
                if (string.suggestions.length) {
                    this.votedSuggestion(string.suggestions.find(suggestion => suggestion.voted));
                } else {
                    this.votedSuggestion(this.newSuggestion);
                }
            } else {
                this.goToNextTranslatableString(0);
            }
        };

        this.goToNextTranslatableString = (startIndex) => {
            let strings = this.translation.strings();
            if (startIndex > 0) {
                strings = strings.slice(startIndex).concat(strings.slice(0, startIndex));
            }
            let translatableString = findTranslatableString(strings);
            if (translatableString) {
                hasher.setHash(`translate/${translatableString.name}`);
            } else {
                // TODO: show translation status
            }
        };

        this.markersInfoText = () => {
            let one = Object.keys(this.string().markers).length === 1;
            return `The <strong>highlighted</strong> marker${one ? ' is' : 's are'} required and mustn't be translated!`;
        };

        this.formatValue = (value) => {
            let escapedValue = html.escape(value);
            for (let marker in this.string().markers) {
                marker = html.escape(marker);
                escapedValue = escapedValue.split(marker).join(`<span class="bg-secondary text-white"><strong>${marker}</strong></span>`);
            }
            return escapedValue;
        };

        this.annotatedMarkers = () => {
            let value = this.string().value;
            if (value instanceof Object) {
                value = value.other;
            }
            var markers = [];
            for (var marker in this.string().markers) {
                var markerDetails = this.string().markers[marker];
                if ('id' in markerDetails) {
                    markers.push([value.indexOf(marker), marker, markerDetails]);
                }
            }
            return markers;
        };

        this.skipString = () => {
            this.goToNextTranslatableString(this.stringIndex + 1);
        };

        this.isSuggestionValid = () => {
            let votedSuggestion = this.votedSuggestion();
            if (!votedSuggestion) {
                return false;
            }
            if (votedSuggestion !== this.newSuggestion) {
                return true;
            }

            function isValid(suggestion) {
                // TODO: make sure markers are not missing
                return suggestion.replace(/\s/g, '').length > 0;
            }

            let value = this.string().value;
            if (value instanceof Object) {
                for (let plural in this.translation.language().plurals) {
                    if (!isValid(this.newSuggestion[plural]())) {
                        return false;
                    }
                }
                return true;
            }

            return isValid(this.newSuggestionOther());
        };

        if (translation.loaded) {
            this.onTranslationLoaded();
        }

        translation.strings.subscribe(strings => {
            this.onTranslationLoaded();
        });
    }

    return {
        template,
        viewModel: ViewModel
    };
});
