<template>
  <div v-if="translation">
    <div class="page-header">
      <h1>{{ project.name }}</h1>
    </div>

    <p>How do you say the following in <strong>{{ language.name }}</strong>?</p>
    <ul class="list-group">
        <li class="string-value list-group-item">{{ string.value }}</li>
    </ul>

    <template v-if="string.suggestions.length">
      <p>Already submitted suggestion{{ string.suggestions.length > 1 ? "s" : "" }}:</p>
      <div class="list-group">
        <a v-for="(suggestion, index) in string.suggestions" :class="['suggestion', 'list-group-item', selectedSuggestion === index ? 'active' : '']" :key="index" @click="selectedSuggestion = index">
            <span :class="['glyphicon', selectedSuggestion === index ? 'glyphicon-check' : 'glyphicon-unchecked']"></span>{{ suggestion.value }}
        </a>
        <a :class="['suggestion', 'list-group-item', selectedSuggestion === -1 ? 'active' : '']" @click="selectedSuggestion = -1">
          <span :class="['state-icon', 'glyphicon', selectedSuggestion === -1 ? 'glyphicon-check' : 'glyphicon-unchecked']"></span><strong>I have a better suggestion...</strong>
        </a>
      </div>
    </template>

    <div v-if="selectedSuggestion === -1">
      <p>My suggestion:</p>
      <div class="form-group">
        <input v-model.trim="translatorSuggestion" type="text" class="form-control" placeholder="Suggestion">
      </div>
    </div>
    
    <div class="form-group">
      <button @click="skipString" class="btn btn-default" type="button">Skip</button>
      <button class="btn btn-primary pull-right" :disabled="!isSuggestionValid()" type="button">Submit</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Translation',

  data() {
    return {
      translation: null,
      selectedString: 106,
      selectedSuggestion: null,
      translatorSuggestion: ''
    };
  },

  computed: {
    project() {
      return this.translation.project;
    },
    language() {
      return this.translation.language;
    },
    string() {
      return this.translation.strings[this.selectedString];
    }
  },

  created() {
    axios
      .get('/api/v1/translations/ff0ad885-4626-4f5d-9aec-5418589136ae:a593b335-ebaf-484f-8ed8-102724e61236')
      .then(response => {
        this.translation = response.data;
      });
  },

  methods: {
    isSuggestionValid() {
      if (this.selectedSuggestion === -1) {
        return this.translatorSuggestion.length > 0;
      }
      return this.selectedSuggestion != null;
    },
    skipString() {
      this.selectedString++;
      if (this.selectedString === this.translation.strings.length) {
        this.selectedString = 0;
      }
      this.selectedSuggestion = null;
      this.translatorSuggestion = '';
    }
  }
};
</script>

<style scoped>
.suggestion {
  padding-left: 3em;
}
.suggestion > .glyphicon {
  position: absolute;
  left: 1em;
  top: 12px;
}
</style>
