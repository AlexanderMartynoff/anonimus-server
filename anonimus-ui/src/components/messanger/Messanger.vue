<template>
  <q-layout view="lHh Lpr lFf" :container="container" class="bg-white">
    <q-header>
      <q-toolbar>
        <q-btn flat icon="menu" class="q-mr-sm" @click="onBtnMenuClick"/>
        <q-toolbar-title>
          Anonimus
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer bordered side="left" :width="leftBarWidth" :breakpoint="leftBarBreakpoint" v-model="showLeftDrawer">
      <q-toolbar class="bg-primary text-white">
        <q-toolbar-title>
          Contacts
        </q-toolbar-title>
      </q-toolbar>
      <messanger-contact-list/>
    </q-drawer>

    <q-page-container>
      <messanger-reader/>
    </q-page-container>

    <q-footer>
      <q-toolbar>
        <messanger-writer/>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script>
import { ref, computed } from 'vue'
import MessangerReader from './MessangerReader.vue'
import MessangerWriter from './MessangerWriter.vue'
import MessangerContactList from './MessangerContactList.vue'

export default {
  name: 'Messanger',
  components: {
    MessangerReader,
    MessangerWriter,
    MessangerContactList,
  },
  props: {
    container: {
      type: Boolean,
    },
    leftBarWidth: {
      type: Number,
      default: 300,
    },
    leftBarBreakpoint: {
      type: Number,
      default: 690,
    },
    members: {
      default: [],
      type: Array,
    },
  },

  setup(props) {
    const showLeftDrawer = ref(true)

    const container = computed(() => props.container)
    const members = computed(() => props.members)
    const leftBarWidth = computed(() => props.leftBarWidth)
    const leftBarBreakpoint = computed(() => props.leftBarBreakpoint)

    return {
      showLeftDrawer,
      leftBarWidth,
      leftBarBreakpoint,
      container,
      members,
      onBtnMenuClick() {
        showLeftDrawer.value = !showLeftDrawer.value
      },
    }
  },
}
</script>
