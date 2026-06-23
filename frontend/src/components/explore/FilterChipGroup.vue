<template>
  <div class="chip-group">
    <div class="filter-group" v-for="f in filterDefs" :key="f.key">
      <button
        class="chip"
        :class="{ on: openKey === f.key }"
        @click.stop="toggle(f.key)"
      >
        {{ f.label }}
        <svg viewBox="0 0 16 16" fill="currentColor" width="11">
          <path d="M8 10L3 5h10l-5 5z"/>
        </svg>
      </button>

      <div v-if="openKey === f.key" class="dropdown">
        <label v-for="o in f.options" :key="o">
          <input
            type="checkbox"
            :checked="modelValue[f.key]?.includes(o)"
            @change="onCheck(f.key, o, $event.target.checked)"
          />
          {{ o }}
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  filterDefs: { type: Array, required: true },
  modelValue: { type: Object, required: true },
})
const emit = defineEmits(['update:modelValue'])

const openKey = ref('')

function toggle(key) {
  openKey.value = openKey.value === key ? '' : key
}

function onCheck(key, value, checked) {
  const current = [...(props.modelValue[key] || [])]
  if (checked) {
    if (!current.includes(value)) current.push(value)
  } else {
    const idx = current.indexOf(value)
    if (idx !== -1) current.splice(idx, 1)
  }
  emit('update:modelValue', { ...props.modelValue, [key]: current })
}

function onClickOutside(e) {
  if (!e.target.closest('.filter-group')) openKey.value = ''
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))
</script>

<style scoped>
.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-group { position: relative; }

.chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 7px 12px;
  border: 1px solid #ddd8cc;
  border-radius: 999px;
  background: #fff;
  font-size: 13px;
  color: #3d3529;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}
.chip:hover, .chip.on {
  border-color: #1e3a5f;
  color: #1e3a5f;
  background: #f0f4f8;
}

.dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  background: #fff;
  border: 1px solid #e8e4d9;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  padding: 8px;
  z-index: 50;
  min-width: 130px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.dropdown label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px;
  font-size: 13px;
  color: #3d3529;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.1s;
}
.dropdown label:hover { background: #f0ece3; }
.dropdown input { accent-color: #1e3a5f; }
</style>