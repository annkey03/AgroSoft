# 🚀 INSTRUCCIONES PARA SUBIR A GITHUB - RamaAngel

## ✅ OPCIÓN 1: Usar el Script Automático

1. **Hacer doble clic** en el archivo `subir_a_github.bat`
2. **Seguir las instrucciones** en pantalla
3. **Introducir credenciales** si Git las pide
4. **¡Listo!** Tu trabajo estará en GitHub

---

## ✅ OPCIÓN 2: Comandos Manuales

### 📋 Paso a Paso:

1. **Abrir Git Bash** (clic derecho → Git Bash Here)

2. **Navegar al proyecto:**
   ```bash
   cd "C:\Users\jbang\OneDrive\Desktop\agrosoft"
   ```

3. **Verificar estado:**
   ```bash
   git status
   ```

4. **Cambiar a tu rama:**
   ```bash
   git checkout RamaAngel
   ```
   
   Si no existe:
   ```bash
   git checkout -b RamaAngel
   ```

5. **Agregar archivos:**
   ```bash
   git add .
   ```

6. **Hacer commit:**
   ```bash
   git commit -m "Sistema AgroSoft completo - RamaAngel"
   ```

7. **Subir a GitHub:**
   ```bash
   git push -u origin RamaAngel
   ```

---

## ✅ OPCIÓN 3: GitHub Desktop

1. **Abrir GitHub Desktop**
2. **Seleccionar repositorio** AgroSoft
3. **Cambiar a rama** RamaAngel (o crearla)
4. **Revisar cambios** en la pestaña Changes
5. **Escribir mensaje** de commit
6. **Commit to RamaAngel**
7. **Push origin**

---

## 📁 ARCHIVOS QUE SE SUBIRÁN

### ✅ Archivos Principales:
- `productores/sipsa_service.py` - Sistema de rentabilidad
- `productores/views.py` - Mensajes graciosos + Funza  
- `productores/datos_reales_service.py` - Fecha corregida
- `templates/recomendaciones.html` - UI mejorada

### ✅ Scripts de Prueba:
- `test_rentabilidad_conservadora.py`
- `test_rango_completo.py`
- `test_funza_y_clima.py`
- `test_mensajes_graciosos.py`
- `test_fecha_actualizacion.py`

---

## 🎯 DESPUÉS DEL PUSH

1. **Ir a GitHub:** https://github.com/tu-usuario/tu-repo
2. **Buscar tu rama:** RamaAngel
3. **Crear Pull Request:** Compare & pull request
4. **Describir cambios:** Usar el mensaje del commit
5. **Asignar revisores:** Tus compañeros de equipo
6. **Esperar aprobación** y hacer merge

---

## 🚨 SI HAY PROBLEMAS

### Error: "Git no reconocido"
- Instalar Git: https://git-scm.com/download/win
- Reiniciar terminal después de instalar

### Error: "Permission denied"
- Configurar credenciales:
  ```bash
  git config --global user.name "Tu Nombre"
  git config --global user.email "tu@email.com"
  ```

### Error: "Conflicts"
- Actualizar main primero:
  ```bash
  git checkout main
  git pull origin main
  git checkout RamaAngel
  git merge main
  ```

### Error: "Remote rejected"
- Verificar permisos en el repositorio
- Contactar al administrador del repo

---

## 💡 COMANDOS ÚTILES

```bash
# Ver diferencias
git diff

# Ver historial
git log --oneline

# Deshacer último commit (mantiene cambios)
git reset HEAD~1

# Ver ramas
git branch -a

# Actualizar desde remoto
git pull origin RamaAngel
```

---

## 📞 AYUDA ADICIONAL

Si necesitas ayuda:
1. **Pregunta a tus compañeros** de equipo
2. **Usa GitHub Desktop** (más visual)
3. **Sube archivos manualmente** desde la web de GitHub
4. **Consulta documentación** de Git

---

## ✅ CHECKLIST FINAL

- [ ] Git instalado y funcionando
- [ ] Repositorio clonado localmente
- [ ] Rama RamaAngel creada
- [ ] Todos los archivos agregados
- [ ] Commit realizado con mensaje descriptivo
- [ ] Push exitoso a GitHub
- [ ] Pull Request creado (opcional)
- [ ] Compañeros notificados

**¡Tu trabajo estará disponible para el equipo una vez completado!** 🎉
