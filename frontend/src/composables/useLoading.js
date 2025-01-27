import { ref, provide, inject } from 'vue'

const LoadingSymbol = Symbol('loading')

export function provideLoading() {
  const isLoading = ref(false)
  const loadingText = ref('')
  const loadingCount = ref(0)

  const startLoading = (text = '加载中...') => {
    loadingCount.value++
    isLoading.value = true
    loadingText.value = text
  }

  const stopLoading = () => {
    loadingCount.value--
    if (loadingCount.value <= 0) {
      loadingCount.value = 0
      isLoading.value = false
      loadingText.value = ''
    }
  }

  provide(LoadingSymbol, {
    isLoading,
    loadingText,
    startLoading,
    stopLoading
  })

  return {
    isLoading,
    loadingText,
    startLoading,
    stopLoading
  }
}

export function useLoading() {
  const loading = inject(LoadingSymbol)
  if (!loading) {
    throw new Error('useLoading must be used after provideLoading')
  }
  return loading
} 