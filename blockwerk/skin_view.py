"""Small textured voxel preview drawn with Qt; no OpenGL dependency."""
import math
from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPolygonF, QTransform
from PySide6.QtWidgets import QWidget
from .skins import modern_skin, part_uv


class SkinPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(220,300)
        self.image=QImage()
        self.variant="classic"
        self.yaw=-25.0
        self._drag=None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setAccessibleName("Skin-Vorschau, mit der Maus drehbar")

    def set_skin(self,image,variant="classic"):
        self.image=modern_skin(image)
        self.variant=variant
        self.update()

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            self._drag=event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self,event):
        if self._drag is not None:
            self.yaw+=(event.position().x()-self._drag.x())*.65
            self._drag=event.position()
            self.update()

    def mouseReleaseEvent(self,event):
        self._drag=None
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform,False)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#17271d"))
        painter.drawRoundedRect(self.rect(),12,12)
        painter.setBrush(QColor(0,0,0,65))
        painter.drawEllipse(QPointF(self.width()/2,self.height()-35),self.width()*.23,10)
        if self.image.isNull():
            painter.end();return
        yaw=math.radians(self.yaw)
        pitch=math.radians(12)
        scale=min(self.width()/25,(self.height()-65)/36)
        def project(point):
            x,y,z=point
            xx=x*math.cos(yaw)+z*math.sin(yaw)
            zz=-x*math.sin(yaw)+z*math.cos(yaw)
            return QPointF(self.width()/2+xx*scale,self.height()/2+5+(-y*math.cos(pitch)+zz*math.sin(pitch))*scale),y*math.sin(pitch)+zz*math.cos(pitch)
        slim=self.variant=="slim"
        arm=3 if slim else 4
        pieces=[("head",(-4,8,4,16,-4,4)),("body",(-4,-4,4,8,-2,2)),
                ("right_arm",(-4-arm,-4,-4,8,-2,2)),("left_arm",(4,-4,4+arm,8,-2,2)),
                ("right_leg",(-4,-16,0,-4,-2,2)),("left_leg",(0,-16,4,-4,-2,2))]
        faces=[]
        for kind,bounds in pieces:
            for outer in (False,True):
                x0,y0,x1,y1,z0,z1=bounds
                expand=(.5 if kind=="head" else .25) if outer else 0
                x0-=expand;x1+=expand;y0-=expand;y1+=expand;z0-=expand;z1+=expand
                shapes={
                    "front":([(x0,y1,z1),(x1,y1,z1),(x1,y0,z1),(x0,y0,z1)],(0,0,1),0),
                    "back":([(x1,y1,z0),(x0,y1,z0),(x0,y0,z0),(x1,y0,z0)],(0,0,-1),30),
                    "left":([(x1,y1,z1),(x1,y1,z0),(x1,y0,z0),(x1,y0,z1)],(1,0,0),45),
                    "right":([(x0,y1,z0),(x0,y1,z1),(x0,y0,z1),(x0,y0,z0)],(-1,0,0),30),
                    "top":([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],(0,1,0),0),
                    "bottom":([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)],(0,-1,0),55)}
                uv=part_uv(kind,slim,outer)
                for face,(corners,normal,shade) in shapes.items():
                    _,depth=project(normal)
                    if depth<=0:continue
                    projected=[project(point) for point in corners]
                    patch=self.image.copy(QRect(*uv[face]))
                    faces.append((sum(p[1] for p in projected)/4,[p[0] for p in projected],patch,shade))
        for _,points,patch,shade in sorted(faces,key=lambda face:face[0]):
            a,b,_,d=points
            transform=QTransform((b.x()-a.x())/patch.width(),(b.y()-a.y())/patch.width(),
                (d.x()-a.x())/patch.height(),(d.y()-a.y())/patch.height(),a.x(),a.y())
            painter.save()
            painter.setTransform(transform)
            painter.drawImage(0,0,patch)
            if shade:
                mask=patch.copy()
                shade_painter=QPainter(mask)
                shade_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                shade_painter.fillRect(mask.rect(),QColor(0,0,0,shade))
                shade_painter.end()
                painter.drawImage(0,0,mask)
            painter.restore()
        painter.setPen(QColor("#9eaea0"))
        painter.drawText(self.rect().adjusted(0,0,0,-9),Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignHCenter,tr("Ziehen zum Drehen"))
        painter.end()
from .i18n import tr
