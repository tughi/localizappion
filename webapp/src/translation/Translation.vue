<template>
  <div v-if="translation">
    <div class="page-header">
      <h1>{{ translation.project.name }}</h1>
    </div>

    <String v-if="typeof string.value === 'string'" :key="stringIndex" :language="language" :skipString="skipString" :string="string" v-on:submit-suggestion="submit" />
    <Plurals v-else :key="stringIndex" :language="language" :skipString="skipString" :string="string" />
  </div>
</template>

<script>
import axios from 'axios';
import Plurals from '@/translation/Plurals';
import String from '@/translation/String';

export default {
  name: 'Translation',

  components: {
    Plurals,
    String
  },

  data() {
    return {
      translation: null,
      stringIndex: 0
    };
  },

  computed: {
    language() {
      return this.translation.language;
    },
    string() {
      return this.translation.strings[this.stringIndex];
    }
  },

  created() {
    axios
      .get(`/api/translators/${this.$route.params.translator}/translations/${this.$route.params.translation}`)
      .then(response => {
        this.translation = response.data;
      });
  },

  methods: {
    skipString() {
      this.stringIndex++;
      if (this.stringIndex === this.translation.strings.length) {
        this.stringIndex = 0;
      }
    },

    submit(suggestion) {
      axios
        .post(`/api/translators/${this.$route.params.translator}/translations/${this.$route.params.translation}`, suggestion)
        .then(response => {
          // TODO: this.translation = response.data;
        });
    }
  }
};
</script>
