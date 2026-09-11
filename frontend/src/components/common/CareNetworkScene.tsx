import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

/**
 * Decorative three.js scene for the login hero: a slowly rotating network of
 * connected nodes, representing the metaphor at the center of the product —
 * one longitudinal record woven from many observations (doctor, caregiver,
 * patient, lab) that only reads as a coherent whole when the links between
 * them are visible. Nodes gently pulse like a heartbeat.
 *
 * This is intentionally the ONLY three.js surface in the app: it lives on
 * the pre-auth hero panel, not inside any clinical workflow, so it never
 * competes with real patient data for a doctor's attention.
 */
export const CareNetworkScene: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const width = mount.clientWidth;
    const height = mount.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
    camera.position.z = 9;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);

    const group = new THREE.Group();
    // Bias the cluster toward the lower-right of the panel — the empty
    // space below the headline — so it never competes with the text.
    group.position.set(1.6, -2.1, 0);
    scene.add(group);

    // Node positions: scattered on a loose sphere shell (organic, not a grid)
    const NODE_COUNT = 22;
    const nodePositions: THREE.Vector3[] = [];
    for (let i = 0; i < NODE_COUNT; i++) {
      const phi = Math.acos(-1 + (2 * i) / NODE_COUNT);
      const theta = Math.sqrt(NODE_COUNT * Math.PI) * phi;
      const radius = 2.2 + Math.random() * 0.5;
      nodePositions.push(
        new THREE.Vector3(
          radius * Math.cos(theta) * Math.sin(phi),
          radius * Math.sin(theta) * Math.sin(phi) * 0.85,
          radius * Math.cos(phi)
        )
      );
    }

    const nodeColor = new THREE.Color('#f4f1ea');
    const nodeGeometry = new THREE.SphereGeometry(0.06, 12, 12);
    const nodeMaterial = new THREE.MeshBasicMaterial({ color: nodeColor, transparent: true, opacity: 0.75 });
    const nodeMeshes: THREE.Mesh[] = nodePositions.map((pos) => {
      const mesh = new THREE.Mesh(nodeGeometry, nodeMaterial);
      mesh.position.copy(pos);
      group.add(mesh);
      return mesh;
    });

    // Connect nodes that are close to each other — the "longitudinal thread"
    const linkGeometryPoints: number[] = [];
    const LINK_DISTANCE = 1.4;
    for (let i = 0; i < nodePositions.length; i++) {
      for (let j = i + 1; j < nodePositions.length; j++) {
        if (nodePositions[i].distanceTo(nodePositions[j]) < LINK_DISTANCE) {
          linkGeometryPoints.push(
            nodePositions[i].x, nodePositions[i].y, nodePositions[i].z,
            nodePositions[j].x, nodePositions[j].y, nodePositions[j].z
          );
        }
      }
    }
    const linkGeometry = new THREE.BufferGeometry();
    linkGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linkGeometryPoints, 3));
    const linkMaterial = new THREE.LineBasicMaterial({ color: '#f4f1ea', transparent: true, opacity: 0.18 });
    const links = new THREE.LineSegments(linkGeometry, linkMaterial);
    group.add(links);

    // eslint-disable-next-line no-console
    console.log('[CareNetworkScene] debug', {
      width, height,
      nodeCount: nodeMeshes.length,
      linkPointCount: linkGeometryPoints.length,
      contextLost: renderer.getContext().isContextLost(),
    });

    let frameId: number;
    let elapsed = 0;
    const clock = new THREE.Clock();

    const animate = () => {
      frameId = requestAnimationFrame(animate);
      const delta = clock.getDelta();
      elapsed += delta;

      if (!prefersReducedMotion) {
        group.rotation.y += delta * 0.08;
        group.rotation.x = Math.sin(elapsed * 0.15) * 0.08;
      }

      // Heartbeat-style pulse across the node field, staggered per node
      nodeMeshes.forEach((mesh, idx) => {
        const phase = elapsed * 1.6 + idx * 0.35;
        const scale = 1 + Math.sin(phase) * 0.28;
        mesh.scale.setScalar(prefersReducedMotion ? 1 : scale);
      });

      try {
        renderer.render(scene, camera);
        if (!(window as any).__cnsLogged) {
          (window as any).__cnsLogged = true;
          // eslint-disable-next-line no-console
          console.log('[CareNetworkScene] render OK', {
            drawingBufferWidth: renderer.domElement.width,
            drawingBufferHeight: renderer.domElement.height,
            canvasInDom: document.body.contains(renderer.domElement),
            clearAlpha: renderer.getClearAlpha(),
            autoClear: renderer.autoClear,
          });
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('[CareNetworkScene] render FAILED', err);
      }
    };
    animate();

    const handleResize = () => {
      if (!mount) return;
      const w = mount.clientWidth;
      const h = mount.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener('resize', handleResize);
      nodeGeometry.dispose();
      nodeMaterial.dispose();
      linkGeometry.dispose();
      linkMaterial.dispose();
      renderer.dispose();
      if (mount.contains(renderer.domElement)) {
        mount.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={mountRef}
      aria-hidden="true"
      style={{
        position: 'absolute',
        inset: 0,
        pointerEvents: 'none',
        zIndex: -1,
      }}
    />
  );
};
