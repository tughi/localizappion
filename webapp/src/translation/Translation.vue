<template>
  <div v-if="translation">
    <div class="page-header">
      <h1>{{ translation.project.name }}</h1>
    </div>

    <String v-if="typeof string.value === 'string'" :key="stringIndex" :language="language" :skipString="skipString" :string="string" />
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
      stringIndex: 106
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
      .get('/api/v1/translations/ff0ad885-4626-4f5d-9aec-5418589136ae:a593b335-ebaf-484f-8ed8-102724e61236')
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
    }
  }
};
</script>
