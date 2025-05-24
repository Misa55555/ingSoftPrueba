# 📌 **Guía de trabajo para el proyecto**

## 🧠 **Explicación general del flujo de trabajo**

1. 🔒 **La rama `main`** solo recibe cambios cuando **todo el grupo valida una sección completa** (vista final y funcional).
2. 🧪 **La rama `test`** sigue el mismo orden que `main`, pero se usa para **probar cambios** antes de que lleguen a producción.
3. 🌿 A partir de `test` se crean **ramas específicas por funcionalidad**, para trabajar sobre cada punto del **Product Backlog**.
4. 🚫 No se debe subir nada que **no esté vinculado directamente al Backlog**.

### 🧱 **Estructura recomendada:**

```
main/
 └── test/
      └── STOCK/
           └── solucion problema de agregado de stock (rama local, no se pushea)
```

1. Trabajás localmente en la rama: `test/STOCK/solucion problema de agregado de stock`
2. Cuando terminás, hacés merge local de esa rama a `STOCK`
3. Pusheás la rama `STOCK`
4. Cuando esté todo bien y revisado, se mergea `STOCK` a `test`
5. Si el grupo aprueba el cambio, finalmente se mergea `test` a `main`

---

## ✅ **Reglas de trabajo**

1. 🚫 No agregar código que no esté en el Backlog
2. 🧾 Usar **la misma sintaxis** en todo el código
3. 🧠 Usar nombres claros para **atributos, funciones y clases**
4. 📝 Documentar **todo lo posible**
5. 📤 **Nunca push de ramas locales**:

   * Creá una rama **local** dentro de la vista que querés modificar
   * Hacés el cambio en esa rama
   * Mergeás esa rama local a la rama (vista) principal
   * Solo ahí hacés push

---

**💡 Recomendación:**
👉 Hacer `git pull` cada vez que se arranca a trabajar
🧹 Eliminar ramas locales que ya no se usen
📖 Leer siempre este README antes de comenzar una nueva tarea

**¡Gracias por mantener el orden! 💪**

---
