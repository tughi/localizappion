<template>
  <div>
    <p>How do you say the following in <strong>{{ language.name }}</strong>?</p>
    <ul class="list-group">
        <li class="list-group-item" v-if="'one' in values"><span v-html="formatValue('one')"></span></li>
        <li class="list-group-item"><span v-html="formatValue('other')"></span></li>
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
  </div>
</template>

<script>
import html from '@/utils/html.js';

export default {
  name: 'TranslatableString',

  props: [
    'language',
    'string'
  ],

  data() {
    return {};
  },

  computed: {
    values() {
      if (typeof this.string.value === 'string') {
        return {
          'other': this.string.value
        };
      }
      return this.string.value;
    },

    annotatedMarkers() {
      var value = this.values['other'];
      var markers = [];
      for (var marker in this.string.markers) {
        var markerDetails = this.string.markers[marker];
        if ('id' in markerDetails) {
          markers.push([value.indexOf(marker), marker, markerDetails]);
        }
      }
      return markers;
    }
  },

  methods: {
    formatValue(pluralForm) {
      var escapedValue = html.escape(this.values[pluralForm]);
      for (var marker in this.string.markers) {
        marker = html.escape(marker);
        escapedValue = escapedValue.split(marker).join(`<span class="bg-info text-info"><strong>${marker}</strong></span>`);
      }
      return escapedValue;
    }
  }
};
</script>
