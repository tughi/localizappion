<template>
  <div>
    <p>How do you say the following in <strong>{{ language.name }}</strong>?</p>
    <ul class="list-group">
        <li class="list-group-item"><span v-html="formattedStringValue"></span></li>
        <li v-if="string.markers" class="list-group-item list-group-item-info">
          <span v-if="Object.keys(string.markers).length === 1">
            The <strong>highlighted</strong> marker is required and cannot be translated
          </span>
          <span v-else>
            The <strong>highlighted</strong> markers are required and cannot be translated
          </span>
        </li>
        <li v-for="marker in annotatedMarkers" :key="marker[1]" class="list-group-item list-group-item-info"><strong>{{ marker[1] }}</strong> - {{ marker[2]['id'] }}</li>
    </ul>
    
    <template v-if="string.suggestions.length">
      <p>Already submitted suggestion{{ string.suggestions.length > 1 ? "s" : "" }}:</p>
      <div class="list-group">
        <a v-for="(suggestion, index) in string.suggestions" :class="['suggestion', 'list-group-item', suggestionIndex === index ? 'active' : '']" :key="index" @click="suggestionIndex = index">
            <span :class="['glyphicon', suggestionIndex === index ? 'glyphicon-check' : 'glyphicon-unchecked']"></span>{{ suggestion.value }}
        </a>
        <a :class="['suggestion', 'list-group-item', suggestionIndex === -2 ? 'active' : '']" @click="suggestionIndex = -2">
          <span :class="['state-icon', 'glyphicon', suggestionIndex === -2 ? 'glyphicon-check' : 'glyphicon-unchecked']"></span><strong>I have a better suggestion...</strong>
        </a>
      </div>
    </template>

    <div v-if="suggestionIndex === -2">
      <p>My suggestion:</p>
      <div class="form-group">
        <input v-model.trim="newSuggestion" type="text" class="form-control" placeholder="Suggestion">
      </div>
    </div>

    <div class="form-group">
      <button @click="skipString" class="btn btn-default" type="button">Skip</button>
      <button class="btn btn-primary pull-right" :disabled="!isSuggestionValid()" type="button">Submit</button>
    </div>
  </div>
</template>

<script>
import html from '@/utils/html.js';

export default {
  name: 'String',

  props: [
    'language',
    'skipString',
    'string'
  ],

  data() {
    return {
      newSuggestion: '',
      suggestionIndex: this.string.suggestions.length === 0 ? -2 : this.string.suggestions.findIndex(suggestion => 'voted' in suggestion)
    };
  },

  computed: {
    annotatedMarkers() {
      var markers = [];
      for (var marker in this.string.markers) {
        var markerDetails = this.string.markers[marker];
        if ('id' in markerDetails) {
          markers.push([this.string.value.indexOf(marker), marker, markerDetails]);
        }
      }
      return markers;
    },

    formattedStringValue() {
      var escapedStringValue = html.escape(this.string.value);
      for (var marker in this.string.markers) {
        marker = html.escape(marker);
        escapedStringValue = escapedStringValue.split(marker).join(`<span class="bg-info text-info"><strong>${marker}</strong></span>`);
      }
      return escapedStringValue;
    }
  },

  methods: {
    isSuggestionValid() {
      return (this.suggestionIndex === -2 && this.newSuggestion.length > 0) || this.suggestionIndex >= 0;
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
