define(['knockout', 'graphql', 'text!./project-detail.html'], function (ko, graphql, template) {
    'use strict';

    function ViewModel(params) {
        this.allProjects = ko.observable();
        this.project = ko.observable();
        this.updatingSuggestion = ko.observable(false);

        const PROJECT_DETAILS = `
            id
            uuid
            newSuggestion {
                id
                translation {
                    language {
                        name
                        pluralForms
                    }
                }
                string {
                    valueOne
                    valueOther
                }
                valueZero
                valueOne
                valueTwo
                valueFew
                valueMany
                valueOther
            }
            newSuggestionsCount
            screenshotsCount
            stringsCount
            translations {
                id
                language {
                    name
                }
                translatedStringsCount
            }
        `;

        graphql({
            query: `
                query ($projectId: ID!) {
                    project(id: $projectId) {
                        ${PROJECT_DETAILS}
                    }
                    allProjects: projects {
                        id
                        name
                    }
                }
            `,
            variables: {
                projectId: params.projectId
            }
        }).then(response => {
            this.allProjects(response.data.allProjects);
            this.project(response.data.project);
        });

        this.updateSuggestion = (suggestion) => {
            this.updatingSuggestion(true);

            graphql({
                query: `
                    mutation ($suggestionId: ID!, $accepted: Boolean!) {
                        updateSuggestion(suggestionId: $suggestionId, accepted: $accepted) {
                            project {
                                ${PROJECT_DETAILS}
                            }
                        }
                    }
                `,
                variables: {
                    suggestionId: suggestion.id,
                    accepted: suggestion.accepted
                }
            }).then(response => {
                this.updatingSuggestion(false);
                this.project(response.data.updateSuggestion.project);
            });
        };

        this.acceptSuggestion = (suggestion) => {
            suggestion.accepted = true;
            this.updateSuggestion(suggestion);
        };

        this.rejectSuggestion = (suggestion) => {
            suggestion.accepted = false;
            this.updateSuggestion(suggestion);
        };
    }

    return {
        template,
        viewModel: ViewModel
    };
});

