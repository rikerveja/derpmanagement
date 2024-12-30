<template>
  <div class="slide-verify" ref="container">
    <div class="slide-verify-block" 
         :class="{ 'success': isSuccess }"
         :style="{ background: background }">
      <span class="slide-verify-text">{{ isSuccess ? successText : text }}</span>
      <div class="slide-verify-slider"
           ref="slider"
           :style="{ left: sliderLeft + 'px', background: sliderBg }"
           @mousedown="handleMouseDown"
           @touchstart="handleTouchStart">
        <span class="slide-verify-slider-icon">→</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SlideVerify',
  props: {
    text: {
      type: String,
      default: '向右滑动验证'
    },
    successText: {
      type: String,
      default: '验证通过'
    },
    background: {
      type: String,
      default: '#f9fafb'
    },
    sliderBg: {
      type: String,
      default: '#7e3af2'
    }
  },
  data() {
    return {
      isSuccess: false,
      sliderLeft: 0,
      startX: 0,
      isDragging: false
    }
  },
  methods: {
    handleMouseDown(e) {
      this.startDrag(e.clientX)
      document.addEventListener('mousemove', this.handleMouseMove)
      document.addEventListener('mouseup', this.handleMouseUp)
    },
    handleMouseMove(e) {
      if (this.isDragging) {
        this.updateSliderPosition(e.clientX)
      }
    },
    handleMouseUp() {
      this.stopDrag()
      document.removeEventListener('mousemove', this.handleMouseMove)
      document.removeEventListener('mouseup', this.handleMouseUp)
    },
    handleTouchStart(e) {
      this.startDrag(e.touches[0].clientX)
      document.addEventListener('touchmove', this.handleTouchMove)
      document.addEventListener('touchend', this.handleTouchEnd)
    },
    handleTouchMove(e) {
      if (this.isDragging) {
        e.preventDefault()
        this.updateSliderPosition(e.touches[0].clientX)
      }
    },
    handleTouchEnd() {
      this.stopDrag()
      document.removeEventListener('touchmove', this.handleTouchMove)
      document.removeEventListener('touchend', this.handleTouchEnd)
    },
    startDrag(clientX) {
      if (this.isSuccess) return
      this.isDragging = true
      this.startX = clientX - this.sliderLeft
    },
    updateSliderPosition(clientX) {
      const container = this.$refs.container
      const slider = this.$refs.slider
      const maxLeft = container.clientWidth - slider.clientWidth
      
      let left = clientX - this.startX
      left = Math.max(0, Math.min(left, maxLeft))
      this.sliderLeft = left

      if (left >= maxLeft - 2) {
        this.isSuccess = true
        this.$emit('success')
      }
    },
    stopDrag() {
      this.isDragging = false
      if (!this.isSuccess) {
        this.sliderLeft = 0
      }
    },
    reset() {
      this.isSuccess = false
      this.sliderLeft = 0
    }
  }
}
</script>

<style scoped>
.slide-verify {
  width: 100%;
  user-select: none;
}

.slide-verify-block {
  position: relative;
  height: 40px;
  background: #f9fafb;
  border: 1px solid #dcdfe6;
  border-radius: 0.25rem;
  overflow: hidden;
}

.slide-verify-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.875rem;
  color: #2c3e50;
  user-select: none;
}

.slide-verify-slider {
  position: absolute;
  top: 0;
  left: 0;
  width: 40px;
  height: 100%;
  background: #7e3af2;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
}

.slide-verify-slider:hover {
  background: #6c2bd9;
}

.slide-verify-slider-icon {
  color: white;
  font-size: 1rem;
}

.success .slide-verify-slider {
  background: #10B981;
}

.success .slide-verify-text {
  color: #10B981;
}
</style> 
